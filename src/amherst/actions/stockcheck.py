from __future__ import annotations

import functools
import time
from collections.abc import Generator
from datetime import date, timedelta
from enum import StrEnum
from pprint import pprint

import matplotlib.pyplot as plt
import pandas as pd
from pawlogger import get_loguru
from pycommence.filters import ConditionType, FieldFilter, FilterArray
from pycommence.pycmc_types import CmcDateFormat, Pagination, RowData
from pycommence.pycommence import PyCommence

from amherst.models.commence_adaptors import HireAliases, HireStatus, RadioType

logger = get_loguru(profile='local')


def filarray_basic():
    return FilterArray.from_filters(
        FieldFilter(column=HireAliases.STATUS, condition=ConditionType.NOT_EQUAL, value=HireStatus.CANCELLED),
        FieldFilter(column=HireAliases.STATUS, condition=ConditionType.NOT_EQUAL, value=HireStatus.RTN_OK),
        FieldFilter(column=HireAliases.STATUS, condition=ConditionType.NOT_EQUAL, value=HireStatus.RTN_PROBLEMS),
        FieldFilter(column=HireAliases.STATUS, condition=ConditionType.NOT_EQUAL, value=HireStatus.PACKED),
        FieldFilter(column=HireAliases.STATUS, condition=ConditionType.NOT_EQUAL, value=HireStatus.QUOTE_GIVEN),
    )


def daterange_generator(start_date, end_date) -> Generator[date, None, None]:
    for delta in range((end_date - start_date).days + 1):
        thisdate = start_date + timedelta(days=delta)
        yield thisdate


class StockChecker:
    def __init__(
        self,
        pycmc=None,
        radiotype: RadioType = None,
        start_date: date = date.today(),
        end_date: date = date.today() + timedelta(days=6),
        stock: int = 500,
        column_to_count: StrEnum = HireAliases.UHF,
    ):
        if radiotype is None and column_to_count == HireAliases.UHF:
            raise ValueError(
                'You must provide a radiotype when checking radio stock. ' 'Use the RadioType enum to specify the type.'
            )
        self.start_date = start_date
        self.end_date = end_date
        self.radiotype = radiotype
        self.column_to_count = column_to_count
        self.stock = stock
        self.pycommence = pycmc or PyCommence.with_csr('Hire')

        self.records = self.get_cmc_data()
        self.data = self.prepare_dataframe()

    def prepare_dataframe(self):
        df = pd.DataFrame(self.records)
        df[HireAliases.SEND_DATE] = pd.to_datetime(
            df[HireAliases.SEND_DATE], format=CmcDateFormat, errors='coerce'
        ).dt.date
        df[HireAliases.DUE_BACK_DATE] = pd.to_datetime(
            df[HireAliases.DUE_BACK_DATE], format=CmcDateFormat, errors='coerce'
        ).dt.date
        # df[HireAliases.UHF] = df[HireAliases.UHF].astype(int)
        df[self.column_to_count] = df[self.column_to_count].astype(int)
        return df

    def get_cmc_data(self):
        pag = Pagination(limit=0, offset=0)
        filter_array = self.get_filter_array()
        records = [
            _.data
            for _ in self.pycommence.read_rows(csrname='Hire', filter_array=filter_array, pagination=pag)
            if isinstance(_, RowData)
        ]
        return records

    def get_filter_array(self):
        filter_array = filarray_basic()
        filter_array.add_filter(
            FieldFilter(
                column=HireAliases.SEND_DATE,
                condition=ConditionType.AFTER,
                value=self.start_date.strftime(CmcDateFormat),
            )
        )
        if self.radiotype:
            filter_array.add_filter(FieldFilter(column=HireAliases.RADIO_TYPE, value=self.radiotype))
        return filter_array

    def run(self):
        dates = list(daterange_generator(self.start_date, self.end_date))
        # dates = list(self.date_range_gen)
        send_data = [self.to_send(datecheck) for datecheck in dates]
        return_data = [self.to_return(datecheck) for datecheck in dates]

        stock_levels = []
        current_stock = self.stock
        for datecheck, send, ret in zip(dates, send_data, return_data):
            current_stock = current_stock - send + ret
            stock_levels.append(current_stock)
            if send or ret:
                logger.info(f'{datecheck}: Sent out={send}, Returned={ret}, Stock left={current_stock}')

        data_df = pd.DataFrame({'Date': dates, 'Send': send_data, 'Return': return_data, 'Stock': stock_levels})

        self.plot_data(data_df)

    def to_send(self, datecheck: date):
        filtered_data = self.data[self.data[HireAliases.SEND_DATE] == datecheck]
        return filtered_data[self.column_to_count].sum()

    def to_return(self, datecheck: date):
        filtered_data = self.data[self.data[HireAliases.DUE_BACK_DATE] == datecheck]
        return filtered_data[self.column_to_count].sum()

    @functools.lru_cache
    def how_many_out(self, datecheck):
        filtered_data = self.data[
            (self.data[HireAliases.SEND_DATE].dt.date < datecheck)
            & (self.data[HireAliases.DUE_BACK_DATE].dt.date > datecheck)
        ]
        rads_out = filtered_data[self.column_to_count].sum()
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
        plt.figure(figsize=(16, 6))

        ax1 = plt.gca()
        ax2 = ax1.twinx()

        ax1.plot(dates, stock, label='Stock Level', color='purple', marker='o')
        ax1.axhline(0, color='red', linestyle='--', linewidth=2, label='Zero Stock')  # Add zero stock line

        ax1.set_xlabel('Date')
        ax1.set_ylabel('Stock Level')
        ax2.set_ylabel('Send/Return Quantity')

        ax1.set_xticks(dates)
        ax1.set_xticklabels([datey.strftime('%d %b') for datey in dates], rotation=90, ha='left')

        ax2.bar(dates, send, width=2, color='blue', label='Send', alpha=0.5)
        ax2.bar(dates, returns, width=2, color='orange', label='Return', alpha=0.5, bottom=send)

        plt.legend(loc='upper left')
        plt.grid(True)
        plt.tight_layout()
        plt.show()


if __name__ == '__main__':
    starttime = time.perf_counter()
    sc = StockChecker(
        radiotype=RadioType.HYTERA,
        column_to_count=HireAliases.PARROT,
        stock=0,
        start_date=date.today(),
        end_date=date.today() + timedelta(days=60),
    )
    sc.run()
    endtime = time.perf_counter()
    print(f'THERE WERE {len(sc.data)} RECORDS')
    print(f'Elapsed time: {endtime - starttime}')
    pprint(sc.data.head(10))
    pprint(sc.data.tail(10))

