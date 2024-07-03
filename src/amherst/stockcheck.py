from __future__ import annotations

import functools
import time
from collections.abc import Generator
from datetime import date, timedelta

import pandas as pd
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from pawlogger import get_loguru

from amherst.commence_adaptors import HireAliases, initial_filter
from pycommence.pycmc_types import CmcDateFormat, RadioType
from pycommence.pycommence_v1 import PyCommence

logger = get_loguru(profile='local')


def prep_df(records):
    df = pd.DataFrame(records)
    df[HireAliases.SEND_OUT_DATE] = pd.to_datetime(df[HireAliases.SEND_OUT_DATE], format=CmcDateFormat, errors='coerce')
    df[HireAliases.DUE_BACK_DATE] = pd.to_datetime(df[HireAliases.DUE_BACK_DATE], format=CmcDateFormat, errors='coerce')
    df[HireAliases.UHF] = df[HireAliases.UHF].astype(int)
    return df


def daterang_gen(start_date, end_date) -> Generator[date, None, None]:
    for x in range((end_date - start_date).days + 1):
        thisdate = start_date + timedelta(days=x)
        yield thisdate


class StockChecker:
    def __init__(
        self,
        pycmc=None,
        radiotype: RadioType = RadioType.HYT,
        start_date: date = date.today(),
        end_date: date = date.today() + timedelta(days=6),
    ):
        self.radiotype = radiotype
        self.start_date = start_date
        self.end_date = end_date
        self.date_range_gen = daterang_gen(start_date, end_date)
        self.pycommence = pycmc or PyCommence.with_csr('Hire', filter_array=self.filters)
        self.data = self._prepare_data()

    def _prepare_data(self):
        records = self.pycommence.rows()
        df = prep_df(records)
        return df

    @property
    def filters(self):
        return initial_filter('Hire')
        # return FilterArray.from_filters(
        #     CmcFilter(cmc_col=HireFields.RADIO_TYPE, condition=ConditionType.EQUAL, value=self.radiotype),
        #     *hires_in_range_fils(self.start_date, self.end_date)
        # )

    def run(self):
        dates = list(self.date_range_gen)
        send_data = [self.to_send(datecheck) for datecheck in dates]
        stock_data = [self.how_many_in(datecheck) for datecheck in dates]
        rads_out = [self.how_many_out(datecheck) for datecheck in dates]

        data_df = pd.DataFrame({'Date': dates, 'Send': send_data, 'Stock': stock_data, 'Out': rads_out})

        self.plot_data(data_df)

    def to_send(self, datecheck: date):
        filtered_data = self.data[(self.data[HireAliases.SEND_OUT_DATE].dt.date == datecheck)]
        return filtered_data[HireAliases.UHF].sum()

    @functools.lru_cache
    def how_many_out(self, datecheck):
        filtered_data = self.data[
            (self.data[HireAliases.SEND_OUT_DATE].dt.date < datecheck)
            & (self.data[HireAliases.DUE_BACK_DATE].dt.date > datecheck)
        ]
        rads_out = filtered_data[HireAliases.UHF].sum()
        return rads_out

    def how_many_in(self, datecheck: date, stock: int = 500):
        rads_out = self.how_many_out(datecheck)
        return stock - rads_out

    def plot_data(self, data_df):
        dates = data_df['Date']
        send = data_df['Send']
        radios_out = data_df['Out']

        ax1 = plt.gca()
        ax2 = ax1.twinx()

        plt.figure()
        # plt.figure(figsize=(14, 7))

        ax2.set_ylim(0, max(send) * 1.1)
        plt.sca(ax2)
        plt.bar(dates, send, width=2, color='blue', label='Send Quantity', alpha=0.7)

        plt.sca(ax1)
        plt.plot(dates, radios_out, label='Rads Out', color='green', marker='o')
        #
        # plt.sca(ax1)
        # plt.plot(dates, radios_in, label='Stock Level', color='green', marker='o')

        ax1.set_xticks(dates)
        ax1.set_xticklabels([datey.strftime('%a %d %b') for datey in dates], rotation=90, ha='right')

        ax1.xaxis.set_major_locator(mdates.DayLocator(interval=3))
        ax1.xaxis.set_major_formatter(mdates.ConciseDateFormatter(ax1.xaxis.get_major_locator()))
        plt.gcf().autofmt_xdate()

        ax1.set_xlabel('Date')
        ax1.set_ylabel(f'{self.radiotype} Radios Out')
        ax2.set_ylabel('Send Out Quantity')

        plt.legend(loc='upper left')
        plt.grid(True)
        plt.show()


if __name__ == '__main__':
    starttime = time.perf_counter()
    sc = StockChecker(
        radiotype=RadioType.HYT,
        start_date=date(2023, 1, 1),
        end_date=date(2024, 7, 1),
    )
    sc.run()
    endtime = time.perf_counter()
    print(f'THERE WERE {len(sc.data)} RECORDS')
    print(f'Elapsed time: {endtime - starttime}')
