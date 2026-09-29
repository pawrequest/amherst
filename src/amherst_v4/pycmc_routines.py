from __future__ import annotations

from datetime import date

from amherst_core.consts_enums import CategoryName
from pycommence import PyCommence
from pycommence.core.filters import ConditionType, FieldFilter, FieldFilterRange, FilterArray
from pycommence.core.row_data import RowData
from pycommence.core.types import CmcDateFormat


async def row_from_pycommence(category: CategoryName, record_name: str) -> RowData:
    with PyCommence(category) as pycmc:
        return pycmc.item_read_csr(pk=record_name)


def row_from_pycommence_sync(category: CategoryName, record_name: str) -> RowData:
    with PyCommence(category) as pycmc:
        return pycmc.item_read_csr(pk=record_name)


def manual_filter():
    f = '[ViewFilter(1, F, , Send Out Date, "Between", "20260601", "20260701")]'
    with PyCommence('Hire') as pycmc:
        csr = pycmc.cursor()
        csr_wrap = csr.cursor_wrapper
        csr_wrap.set_filter(f)
        res_ = csr.read_rows()
        yield from res_


def test_manual():
    res = list(manual_filter())
    print(len(res))
    print([_.data['Send Out Date'] for _ in res if isinstance(_, RowData)])


def get_daterange(table_name: str, field_name: str, start_date: date, end_date: date):
    start = start_date.strftime(CmcDateFormat)
    end = end_date.strftime(CmcDateFormat)
    with PyCommence(table_name) as pycmc:
        filter_array = FilterArray.from_filters(
            FieldFilterRange(column=field_name, condition=ConditionType.BETWEEN, value=start, value_max=end)
        )
        yield from pycmc.cursor().read_rows(filter_array=filter_array)


def test_dateranger():
    end_date = date(2026, 7, 1)
    start_date = date(2026, 6, 1)
    res_ = get_daterange('Hire', 'Send Out Date', start_date, end_date)
    res_ = list(res_)
    print(len(res_))
    send_dates = [_.data['Send Out Date'] for _ in res_ if isinstance(_, RowData)]
    send_dates = [date.fromisoformat(_) for _ in send_dates]
    assert all([start_date <= _ <= end_date for _ in send_dates])


if __name__ == '__main__':
    test_dateranger()
