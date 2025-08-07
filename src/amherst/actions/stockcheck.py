from __future__ import annotations

import functools
import time
from collections.abc import Generator
from datetime import date, timedelta
from enum import StrEnum

import matplotlib.pyplot as plt
import pandas as pd
from pawlogger import get_loguru
from pycommence.filters import FilterArray
from pycommence.pycmc_types import CmcDateFormat, MoreAvailable, Pagination, RowData
from pycommence.pycommence import PyCommence

from amherst.actions.one_shots import good_hires_fils
from amherst.models.commence_adaptors import HireAliases
from amherst.models.filters import HIRE_ARRAY_LOOSE

logger = get_loguru(profile='local')


def prep_df(records):
    df = pd.DataFrame(records)
    df[HireAliases.SEND_DATE] = pd.to_datetime(df[HireAliases.SEND_DATE], format=CmcDateFormat, errors='coerce').dt.date
    df[HireAliases.DUE_BACK_DATE] = pd.to_datetime(
        df[HireAliases.DUE_BACK_DATE], format=CmcDateFormat, errors='coerce'
    ).dt.date
    df[HireAliases.UHF] = df[HireAliases.UHF].astype(int)
    return df


# def prep_df(records):
#     df = pd.DataFrame(records)
#     df[HireAliases.SEND_DATE] = pd.to_datetime(df[HireAliases.SEND_DATE], format=CmcDateFormat, errors='coerce')
#     df[HireAliases.DUE_BACK_DATE] = pd.to_datetime(df[HireAliases.DUE_BACK_DATE], format=CmcDateFormat, errors='coerce')
#     df[HireAliases.UHF] = df[HireAliases.UHF].astype(int)
#     return df


def daterang_gen(start_date, end_date) -> Generator[date, None, None]:
    for x in range((end_date - start_date).days + 1):
        thisdate = start_date + timedelta(days=x)
        yield thisdate


class RadioType(StrEnum):
    HYT = 'HYT'
    HYTERA = 'HYTERA'
    MOTOROLA = 'MOTOROLA'
    ICOM = 'ICOM'
    KENWOOD = 'KENWOOD'
    UNIDEN = 'UNIDEN'
    OTHER = 'OTHER'



class StockChecker:
    def __init__(
        self,
        pycmc=None,
        radiotype: RadioType = RadioType.HYT,
        start_date: date = date.today(),
        end_date: date = date.today() + timedelta(days=6),
        stock: int = 500,
    ):
        self.radiotype = radiotype
        self.stock = stock
        self.date_range_gen = daterang_gen(start_date, end_date)
        self.pycommence = pycmc or PyCommence.with_csr('Hire')
        self.data = self._prepare_data()

    def _prepare_data(self):
        pag = Pagination(limit=0, offset=0)
        filter_array = FilterArray.from_filters(*good_hires_fils())
        records = [
            _.data
            for _ in self.pycommence.read_rows(csrname='Hire', filter_array=filter_array, pagination=pag)
            if isinstance(_, RowData)
        ]
        df = prep_df(records)
        return df

    @property
    def filters(self):
        # todo break this
        return HIRE_ARRAY_LOOSE
        # return get_filter_array('Hire')

    def run(self):
        dates = list(self.date_range_gen)
        send_data = [self.to_send(datecheck) for datecheck in dates]
        return_data = [self.to_return(datecheck) for datecheck in dates]

        stock_levels = []
        current_stock = self.stock
        for datecheck, send, ret in zip(dates, send_data, return_data):
            current_stock = current_stock - send + ret
            stock_levels.append(current_stock)
            logger.info(f'{datecheck}: Sent out={send}, Returned={ret}, Stock left={current_stock}')

        data_df = pd.DataFrame({'Date': dates, 'Send': send_data, 'Return': return_data, 'Stock': stock_levels})

        self.plot_data(data_df)

    # def run(self):
    #     dates = list(self.date_range_gen)
    #     send_data = [self.to_send(datecheck) for datecheck in dates]
    #     return_data = [self.to_return(datecheck) for datecheck in dates]
    #
    #     stock_levels = []
    #     current_stock = self.stock
    #     for send, ret in zip(send_data, return_data):
    #         current_stock = current_stock - send + ret
    #         stock_levels.append(current_stock)
    #
    #     data_df = pd.DataFrame({'Date': dates, 'Send': send_data, 'Return': return_data, 'Stock': stock_levels})
    #
    #     self.plot_data(data_df)
    def to_send(self, datecheck: date):
        filtered_data = self.data[self.data[HireAliases.SEND_DATE] == datecheck]
        return filtered_data[HireAliases.UHF].sum()

    def to_return(self, datecheck: date):
        filtered_data = self.data[self.data[HireAliases.DUE_BACK_DATE] == datecheck]
        return filtered_data[HireAliases.UHF].sum()

    # def to_return(self, datecheck: date):
    #     filtered_data = self.data[self.data[HireAliases.DUE_BACK_DATE].dt.date == datecheck]
    #     return filtered_data[HireAliases.UHF].sum()

    #
    # def run(self):
    #     dates = list(self.date_range_gen)
    #     send_data = [self.to_send(datecheck) for datecheck in dates]
    #     rads_in = [self.how_many_in(datecheck) for datecheck in dates]
    #     rads_out = [self.how_many_out(datecheck) for datecheck in dates]
    #
    #     data_df = pd.DataFrame({'Date': dates, 'Send': send_data, 'In': rads_in, 'Out': rads_out})
    #
    #     self.plot_data(data_df)

    # def to_send(self, datecheck: date):
    #     filtered_data = self.data[(self.data[HireAliases.SEND_DATE].dt.date == datecheck)]
    #     return filtered_data[HireAliases.UHF].sum()

    @functools.lru_cache
    def how_many_out(self, datecheck):
        filtered_data = self.data[
            (self.data[HireAliases.SEND_DATE].dt.date < datecheck)
            & (self.data[HireAliases.DUE_BACK_DATE].dt.date > datecheck)
        ]
        rads_out = filtered_data[HireAliases.UHF].sum()
        return rads_out

    def how_many_in(self, datecheck: date, stock: int = None):
        stock = stock or self.stock
        rads_out = self.how_many_out(datecheck)
        return stock - rads_out

    def plot_data(self, data_df):
        dates = data_df['Date']
        send = data_df['Send']
        returns = data_df['Return']
        stock = data_df['Stock']

        plt.figure()
        ax1 = plt.gca()
        ax2 = ax1.twinx()

        ax1.plot(dates, stock, label='Stock Level', color='purple', marker='o')
        ax2.bar(dates, send, width=2, color='blue', label='Send Quantity', alpha=0.7)
        ax2.bar(dates, returns, width=2, color='orange', label='Return Quantity', alpha=0.5, bottom=send)

        ax1.set_xlabel('Date')
        ax1.set_ylabel('Stock Level')
        ax2.set_ylabel('Send/Return Quantity')

        ax1.set_xticks(dates)
        ax1.set_xticklabels([datey.strftime('%a %d %b') for datey in dates], rotation=90, ha='right')

        plt.legend(loc='upper left')
        plt.grid(True)
        plt.show()

    # def plot_data(self, data_df):
    #     dates = data_df['Date']
    #     send = data_df['Send']
    #     radios_out = data_df['Out']
    #     radios_in = data_df['In']
    #
    #     max_value = max(max(send), max(radios_out))
    #
    #     plt.figure()
    #     # plt.figure(figsize=(14, 7))
    #
    #     ax1 = plt.gca()
    #     ax2 = ax1.twinx()
    #
    #     ax1.set_ylim(0, max_value * 1.1)
    #     ax2.set_ylim(0, max_value * 1.1)
    #
    #     max_radios_out_value = max(radios_out)
    #     max_radios_out_date = dates[radios_out.idxmax()]
    #
    #     plt.sca(ax2)
    #     plt.bar(dates, send, width=2, color='blue', label='Send Quantity', alpha=0.7)
    #
    #     plt.sca(ax1)
    #     # for i, date in enumerate(dates):
    #     #     color = 'red' if radios_out[i] > self.stock or radios_in[i] < 0 else 'green'
    #     #     plt.plot(date, radios_out[i], marker='o', color=color)
    #     #     plt.plot(date, radios_in[i], marker='o', color=color if radios_in[i] < 0 else 'none')
    #     plt.plot(dates, radios_in, label='Rads In', color='green', marker='o')
    #     plt.plot(dates, radios_out, label='Rads Out', color='blue', marker='o')
    #
    #     # for datey, s, ro in zip(dates, send, radios_out):
    #     #     if s > self.stock:
    #     #         ax2.annotate(f'{s}', xy=(datey, s), xytext=(datey, s * 1.05), ha='center', color='red')
    #     #     if ro > self.stock:
    #     #         ax1.annotate(f'{ro}', xy=(datey, ro), xytext=(datey, ro * 1.05), ha='center', color='red')
    #
    #     for i, (datey, s, ro) in enumerate(zip(dates, send, radios_out)):
    #         if s > self.stock:
    #             ax2.annotate(
    #                 f'{s}',
    #                 xy=(datey, s),
    #                 xytext=(datey, s * (1.05 + 0.05 * (i % 2))),
    #                 ha='center',
    #                 color='red',
    #                 fontsize=9,
    #                 bbox=dict(facecolor='white', alpha=0.5, edgecolor='red'),
    #             )
    #         if ro > self.stock:
    #             ax1.annotate(
    #                 f'{ro}',
    #                 xy=(datey, ro),
    #                 xytext=(datey, ro * (1.05 + 0.05 * (i % 2))),
    #                 ha='center',
    #                 color='red',
    #                 fontsize=9,
    #                 bbox=dict(facecolor='white', alpha=0.5, edgecolor='red'),
    #             )
    #
    #     # ax1.annotate(
    #     #     f'{max_radios_out_value}',
    #     #     xy=(max_radios_out_date, max_radios_out_value),
    #     #     xytext=(max_radios_out_date, max_radios_out_value + 0.05 * max_value),
    #     #     arrowprops=dict(facecolor='green', shrink=0.05),
    #     # )
    #     ax1.set_xticks(dates)
    #     ax1.set_xticklabels([datey.strftime('%a %d %b') for datey in dates], rotation=90, ha='right')
    #
    #     # ax1.xaxis.set_major_locator(mdates.DayLocator(interval=3))
    #     ax1.xaxis.set_major_formatter(mdates.ConciseDateFormatter(ax1.xaxis.get_major_locator()))
    #     plt.gcf().autofmt_xdate()
    #
    #     ax1.set_xlabel('Date')
    #     ax1.set_ylabel(f'{self.radiotype} Radios Out')
    #
    #     ax2.set_ylabel('Send Out Quantity')
    #
    #     plt.legend(loc='upper left')
    #     plt.grid(True)
    #     plt.show()


if __name__ == '__main__':
    starttime = time.perf_counter()
    sc = StockChecker(
        radiotype=RadioType.HYT,
        stock=200,
        start_date=date(2025, 8, 7),
        end_date=date(2025, 8, 21),
    )
    sc.run()
    endtime = time.perf_counter()
    print(f'THERE WERE {len(sc.data)} RECORDS')
    print(f'Elapsed time: {endtime - starttime}')
