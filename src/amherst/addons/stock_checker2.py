"""
stock_checker2.py — Rewritten stock availability checker.

Improvements over the original stockcheck.py:
  - Snapshot model: for each day, count units currently out (send_date ≤ day ≤ due_back_date).
    The original BETWEEN filter silently missed hires that *span across* the query window.
  - Separation of concerns: fetch / calculate / display are independent functions.
  - Pydantic config with sensible defaults.
  - Rich terminal table alongside the matplotlib chart.
  - Negative / near-zero stock flagged in the table and logged as warnings.
  - Fleet total is *derived* from in-hand stock + units currently out, so the user only
    needs to supply what they can physically count in the warehouse.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import date, timedelta

import matplotlib.pyplot as plt
import pandas as pd
from amherst_core.consts_enums import HireStatus, RadioType
from amherst_core.models import AmherstHire
from amherst_core.utils.get_set_convert import alias_lookup
from pawlogger import get_loguru
from pycommence import PyCommence
from pycommence.core.filters import ConditionType, FieldFilter, FilterArray
from pycommence.core.pagination import Pagination
from pycommence.core.row_data import RowData
from pycommence.core.types import CmcDateFormat
from pydantic import BaseModel, Field
from rich.console import Console
from rich.table import Table
from rich.text import Text

logger = get_loguru(profile='local')

# ── Commence field aliases ──────────────────────────────────────────────────
_STATUS_COL = alias_lookup(AmherstHire, 'status')
_SEND_COL = alias_lookup(AmherstHire, 'send_date')
_DUE_BACK_COL = alias_lookup(AmherstHire, 'due_back_date')
_RADIO_TYPE_COL = alias_lookup(AmherstHire, 'radio_type')
_NAME_COL = alias_lookup(AmherstHire, 'name')

_ALWAYS_EXCLUDED: list[HireStatus] = [
    HireStatus.CANCELLED,
    HireStatus.RTN_OK,
    HireStatus.RTN_PROBLEMS,
    HireStatus.PACKED,
]


# ── Config ──────────────────────────────────────────────────────────────────
class StockCheckConfig(BaseModel):
    """Parameters for a single stock-check run.

    Supply ``stock_in_hand``: how many units are physically sitting in the warehouse
    right now (today).  The total fleet size is then derived automatically as
    ``stock_in_hand + units_currently_out_on_hire``, so you don't need to track
    the full fleet number separately.

    Set ``exclude_quotes=False`` to include Quote-Given hires in the stock count
    (i.e. treat them as potential demand on stock).
    """

    category: str = 'Hire'
    radio_type: RadioType | None = None
    start_date: date = Field(default_factory=date.today)
    end_date: date = Field(default_factory=lambda: date.today() + timedelta(days=90))
    stock_in_hand: int                   # units physically in the warehouse today
    count_field: str = 'Number UHF'
    exclude_quotes: bool = True          # if True, Quote-Given hires are ignored

    @property
    def excluded_statuses(self) -> list[HireStatus]:
        statuses = list(_ALWAYS_EXCLUDED)
        if self.exclude_quotes:
            statuses.append(HireStatus.QUOTE_GIVEN)
        return statuses

    @property
    def label(self) -> str:
        return self.radio_type.value if self.radio_type else self.count_field


# ── Data layer ───────────────────────────────────────────────────────────────
def _build_filter_array(config: StockCheckConfig) -> FilterArray:
    """Exclude terminal statuses + optionally filter by radio type."""
    filters = [
        FieldFilter(column=_STATUS_COL, condition=ConditionType.NOT_EQUAL, value=s)
        for s in config.excluded_statuses
    ]
    if config.radio_type:
        filters.append(FieldFilter(column=_RADIO_TYPE_COL, value=config.radio_type))
    return FilterArray.from_filters(*filters)


def fetch_hire_df(config: StockCheckConfig, pycmc: PyCommence) -> pd.DataFrame:
    """
    Fetch active hire records from Commence and return a clean DataFrame.

    Date filtering is intentionally done in Python — Commence's BETWEEN filter
    only matches records whose due_back_date falls *within* the queried window,
    silently omitting hires that span across the start or end of the window.
    """
    filter_array = _build_filter_array(config)
    csr = pycmc.cursor(config.category)

    records = [
        row.data
        for row in csr.read_rows(filter_array=filter_array, pagination=Pagination(limit=0))
        if isinstance(row, RowData)
    ]

    if not records:
        logger.warning('No hire records returned from Commence.')
        return pd.DataFrame()

    df = pd.DataFrame(records)
    df[_SEND_COL] = pd.to_datetime(df[_SEND_COL], format=CmcDateFormat, errors='coerce').dt.date
    df[_DUE_BACK_COL] = pd.to_datetime(df[_DUE_BACK_COL], format=CmcDateFormat, errors='coerce').dt.date
    df[config.count_field] = pd.to_numeric(df[config.count_field], errors='coerce').fillna(0).astype(int)
    df = df.dropna(subset=[_SEND_COL, _DUE_BACK_COL])

    logger.info(f'Fetched {len(df)} active hire records from Commence.')
    return df


def derive_fleet_total(df: pd.DataFrame, config: StockCheckConfig) -> int:
    """
    Compute the true fleet size: units in hand today + units currently out on hire.

    This means the user only needs to count what's physically in the warehouse —
    the code works out the rest from Commence.
    """
    today = date.today()
    if df.empty:
        logger.warning('DataFrame is empty; fleet total = stock_in_hand only.')
        return config.stock_in_hand

    out_today_mask = (df[_SEND_COL] <= today) & (df[_DUE_BACK_COL] >= today)
    units_out_today = int(df.loc[out_today_mask, config.count_field].sum())
    fleet_total = config.stock_in_hand + units_out_today

    logger.info(
        f'Fleet total derived: {fleet_total}  '
        f'({config.stock_in_hand} in hand  +  {units_out_today} currently out on hire)'
    )
    return fleet_total


# ── Snapshot model ───────────────────────────────────────────────────────────
@dataclass
class DailySnapshot:
    date: date
    sending: int          # units going out this day
    returning: int        # units coming back this day
    units_out: int        # total units currently on hire (snapshot)
    available: int        # fleet_total - units_out
    active_hirers: list[tuple[str, int]] = field(default_factory=list)  # (name, units)


def calculate_snapshots(
    df: pd.DataFrame, config: StockCheckConfig, fleet_total: int
) -> list[DailySnapshot]:
    """
    Snapshot model: for each day, count units on hire where send_date ≤ day ≤ due_back_date.

    Correctly handles hires that begin before or end after the query window.
    Logs a WARNING for any day where available stock reaches zero or below.
    """
    snapshots: list[DailySnapshot] = []
    total_days = (config.end_date - config.start_date).days + 1

    for delta in range(total_days):
        day = config.start_date + timedelta(days=delta)

        if df.empty:
            snapshots.append(
                DailySnapshot(date=day, sending=0, returning=0, units_out=0, available=fleet_total)
            )
            continue

        out_mask = (df[_SEND_COL] <= day) & (df[_DUE_BACK_COL] >= day)
        send_mask = df[_SEND_COL] == day
        return_mask = df[_DUE_BACK_COL] == day

        units_out = int(df.loc[out_mask, config.count_field].sum())
        sending = int(df.loc[send_mask, config.count_field].sum())
        returning = int(df.loc[return_mask, config.count_field].sum())
        available = fleet_total - units_out

        hirers: list[tuple[str, int]] = sorted(
            (
                (name, units)
                for name, units in zip(
                    df.loc[out_mask, _NAME_COL],
                    df.loc[out_mask, config.count_field],
                )
            ),
            key=lambda x: x[1],
            reverse=True,
        )

        if available <= 0:
            logger.warning(
                f'{day}: STOCK EXHAUSTED — {units_out} out of {fleet_total}, available={available}'
            )
        elif available <= fleet_total * 0.1:
            logger.warning(f'{day}: Low stock — {available} remaining out of {fleet_total}.')

        snapshots.append(
            DailySnapshot(
                date=day,
                sending=sending,
                returning=returning,
                units_out=units_out,
                available=available,
                active_hirers=hirers,
            )
        )

    return snapshots


# ── Terminal output ──────────────────────────────────────────────────────────
def _available_text(available: int, fleet_total: int) -> Text:
    """Colour-code the available stock figure."""
    if available <= 0:
        return Text(str(available), style='bold red')
    if available <= fleet_total * 0.1:
        return Text(str(available), style='bold yellow')
    return Text(str(available), style='green')


def _truncate(name: str, max_chars: int = 20) -> str:
    return name[:max_chars] + '…' if len(name) > max_chars else name


def _hirers_cell(hirers: list[tuple[str, int]], max_show: int = 3) -> str:
    if not hirers:
        return '—'
    shown = ', '.join(f'{_truncate(name)} ({units})' for name, units in hirers[:max_show])
    if len(hirers) > max_show:
        shown += f'  +{len(hirers) - max_show} more'
    return shown


def print_rich_table(
    snapshots: list[DailySnapshot], config: StockCheckConfig, fleet_total: int
) -> None:
    """Print a Rich table of daily snapshots to stdout."""
    console = Console()
    table = Table(
        title=(
            f'Stock Check — {config.label}  ({config.start_date} → {config.end_date})'
            f'   fleet: {fleet_total}  |  in hand today: {config.stock_in_hand}'
        ),
        show_lines=False,
        header_style='bold',
    )
    table.add_column('Date', style='cyan', no_wrap=True)
    table.add_column('Sending', justify='right', style='blue')
    table.add_column('Returning', justify='right', style='dark_orange')
    table.add_column('Units Out', justify='right')
    table.add_column('Available', justify='right')
    table.add_column('Hirers Out', no_wrap=False, max_width=60)

    for snap in snapshots:
        row_style = 'dim' if not snap.sending and not snap.returning else ''
        table.add_row(
            snap.date.strftime('%a %d %b'),
            str(snap.sending) if snap.sending else '—',
            str(snap.returning) if snap.returning else '—',
            str(snap.units_out),
            _available_text(snap.available, fleet_total),
            _hirers_cell(snap.active_hirers),
            style=row_style,
        )

    # summary footer
    total_sends = sum(s.sending for s in snapshots)
    total_returns = sum(s.returning for s in snapshots)
    min_available = min(s.available for s in snapshots)
    table.add_section()
    table.add_row(
        'TOTAL / MIN',
        str(total_sends),
        str(total_returns),
        '',
        _available_text(min_available, fleet_total),
        f'fleet pool: {fleet_total}',
        style='bold',
    )

    console.print(table)


# ── Visualisation ────────────────────────────────────────────────────────────
def plot_snapshots(
    snapshots: list[DailySnapshot], config: StockCheckConfig, fleet_total: int
) -> None:
    """Single-axis chart: available stock line + send/return bars, all in the same unit."""
    dates = [s.date for s in snapshots]
    available = [s.available for s in snapshots]
    sending = [s.sending for s in snapshots]
    returning = [s.returning for s in snapshots]
    warn_threshold = fleet_total * 0.1

    fig, ax = plt.subplots(figsize=(16, 6))

    # Bars first so the stock line renders on top
    ax.bar(dates, sending, width=0.4, color='steelblue', label='Sending', alpha=0.7, align='edge')
    ax.bar(dates, returning, width=-0.4, color='darkorange', label='Returning', alpha=0.7, align='edge')

    ax.plot(dates, available, label='Stock Available', color='purple', marker='o', zorder=3, linewidth=2)
    ax.axhline(0, color='red', linestyle='--', linewidth=2, label='Zero Stock')
    ax.axhline(warn_threshold, color='orange', linestyle=':', linewidth=1.5, label='10% Warning')

    ax.fill_between(
        dates,
        available,
        0,
        where=[a < 0 for a in available],
        color='red',
        alpha=0.25,
        label='Overbooked',
    )

    ax.set_xlabel('Date')
    ax.set_ylabel('Units')
    ax.set_xticks(dates)
    ax.set_xticklabels([d.strftime('%d %b') for d in dates], rotation=90, ha='right')
    ax.legend(loc='upper left')

    plt.title(
        f'{config.label} — Stock Availability  {config.start_date} to {config.end_date}'
        f'  (fleet: {fleet_total})'
    )
    plt.grid(True, axis='y', alpha=0.3)
    plt.tight_layout()
    plt.show()


# ── Orchestrator ─────────────────────────────────────────────────────────────
def _do_check(config: StockCheckConfig, pycmc: PyCommence) -> list[DailySnapshot]:
    df = fetch_hire_df(config, pycmc)
    fleet_total = derive_fleet_total(df, config)
    snapshots = calculate_snapshots(df, config, fleet_total)
    print_rich_table(snapshots, config, fleet_total)
    plot_snapshots(snapshots, config, fleet_total)
    return snapshots


def run_stock_check(config: StockCheckConfig, pycmc: PyCommence | None = None) -> list[DailySnapshot]:
    """
    Fetch → calculate → display.

    Pass an existing *open* PyCommence instance to reuse a connection,
    or omit it and this function will open and close one itself.
    """
    if pycmc is not None:
        return _do_check(config, pycmc)
    with PyCommence(config.category) as cmc:
        return _do_check(config, cmc)


# ── Entry point ──────────────────────────────────────────────────────────────
if __name__ == '__main__':
    _t0 = time.perf_counter()

    _config = StockCheckConfig(
        radio_type=RadioType.HYTERA,
        stock_in_hand=300,   # units physically in the warehouse right now
        start_date=date.today(),
        end_date=date.today() + timedelta(days=30),
        exclude_quotes=False,
    )

    with PyCommence(_config.category) as _pycmc:
        _snapshots = run_stock_check(_config, _pycmc)

    print(f'\nChecked {len(_snapshots)} days  |  elapsed: {time.perf_counter() - _t0:.2f}s')

