from collections.abc import Generator
from datetime import date, timedelta

import pandas as pd
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from pawlogger import get_loguru

from amherst.commence import HireFields, HireStatus
from pycommence.pyc2 import PyCommence
from pycommence.pycmc_types import CmcFilter, ConditionType, FilterArray, RadioType, to_cmc_date, CmcDateFormat

logger = get_loguru(profile='local')


def daterang_gen(start_date, end_date) -> Generator[date, None, None]:
    for x in range((end_date - start_date).days + 1):
        thisdate = start_date + timedelta(days=x)
        yield thisdate


def good_hires_fils():
    return (
        CmcFilter(cmc_col=HireFields.STATUS, condition=ConditionType.NOT_EQUAL, value=HireStatus.CANCELLED),
        CmcFilter(cmc_col=HireFields.STATUS, condition=ConditionType.NOT_EQUAL, value=HireStatus.RTN_OK),
        CmcFilter(cmc_col=HireFields.STATUS, condition=ConditionType.NOT_EQUAL, value=HireStatus.RTN_PROBLEMS),
    )


def good_hires_in_range_array(start_date: date, end_date: date, radiotype=RadioType.HYT):
    return FilterArray.from_filters(
        *good_hires_fils(),
        CmcFilter(cmc_col=HireFields.SEND_OUT_DATE, condition=ConditionType.BEFORE, value=to_cmc_date(end_date)),
        CmcFilter(cmc_col=HireFields.DUE_BACK_DATE, condition=ConditionType.AFTER, value=to_cmc_date(start_date)),
        CmcFilter(cmc_col=HireFields.RADIO_TYPE, condition=ConditionType.EQUAL, value=radiotype),
    )


#
# class StockChecker:
#     def __init__(self, pycmc=None, start_date: date = date.today(), end_date: date = date.today() + timedelta(days=6)):
#         self.pycommence = pycmc or PyCommence.with_csr(
#             'Hire',
#             filter_array=good_hires_in_range_array(start_date, end_date)
#         )
#         self.start_date = start_date
#         self.end_date = end_date
#         self.date_range_gen = daterang_gen(start_date, end_date)
#         self.data = self._load_data()
#
#     def _load_data(self):
#         records = self.pycommence.records()
#         return pd.DataFrame(records)
#
#     def to_send(self, datecheck: date, radiotype=RadioType.HYT):
#         """How many radios to send on a given date"""
#         filtered_data = self.data[
#             (self.data[HireFields.SEND_OUT_DATE] == datecheck.isoformat()) &
#             (self.data[HireFields.RADIO_TYPE] == radiotype)
#             ]
#         return filtered_data[HireFields.UHF].astype(int).sum()
#
#     def how_many_in(self, datecheck: date, radiotype=RadioType.HYT, stock: int = 500):
#         filtered_data = self.data[
#             (self.data[HireFields.SEND_OUT_DATE] < datecheck.isoformat()) &
#             (self.data[HireFields.DUE_BACK_DATE] > datecheck.isoformat()) &
#             (self.data[HireFields.RADIO_TYPE] == radiotype)
#             ]
#         rads_out = filtered_data[HireFields.UHF].astype(int).sum()
#         return stock - rads_out
#
#     def get_mat_data(self):
#         data = []
#         for datecheck in self.date_range_gen:
#             send = self.to_send(datecheck)
#             rads_in = self.how_many_in(datecheck)
#             data.append((datecheck, send, rads_in))
#         return data
#
#     def run(self):
#         data = self.get_mat_data()
#
#         dates = [d[0] for d in data]
#         send = [d[1] for d in data]
#         radios_in = [d[2] for d in data]
#
#         ax1 = plt.gca()
#         ax2 = ax1.twinx()
#
#         # Plotting the data
#         plt.figure(figsize=(14, 7))
#
#         ax2.set_ylim(0, max(send) * 1.1)
#         plt.sca(ax2)
#         plt.bar(dates, send, width=0.4, color='blue', label='Send Quantity', alpha=0.7)
#
#         plt.sca(ax1)
#         plt.plot(dates, radios_in, label='Stock Level', color='green', marker='o')
#
#         ax1.set_xticks(dates)
#         ax1.set_xticklabels([datey.strftime('%a %d %b') for datey in dates], rotation=90, ha='right')
#
#         ax1.xaxis.set_major_locator(mdates.DayLocator(interval=3))
#         ax1.xaxis.set_major_formatter(mdates.ConciseDateFormatter(ax1.xaxis.get_major_locator()))
#         plt.gcf().autofmt_xdate()
#
#         ax1.set_xlabel('Date')
#         ax1.set_ylabel('Stock Remaining')
#         ax2.set_ylabel('Send Out Quantity')
#
#         plt.legend(loc='upper left')
#         plt.grid(True)
#         plt.show()

# ax1 = plt.gca()
# ax2 = ax1.twinx()
#
# plt.figure(figsize=(14, 7))
#
# ax2.set_ylim(0, max(send) * 1.1)
# plt.sca(ax2)
# plt.bar(dates, send, width=0.4, color='blue', label='Send Quantity', alpha=0.7)
#
# plt.sca(ax1)
# plt.plot(dates, radios_in, label='Stock Level', color='green', marker='o')
#
# ax1.set_xticks(dates)
# ax1.set_xticklabels([datey.strftime('%a %d %b') for datey in dates], rotation=90, ha='right')
#
# ax1.xaxis.set_major_locator(mdates.DayLocator(interval=3))
# ax1.xaxis.set_major_formatter(mdates.ConciseDateFormatter(ax1.xaxis.get_major_locator()))
# plt.gcf().autofmt_xdate()
#
# ax1.set_xlabel('Date')
# ax1.set_ylabel('Stock Remaining')
# ax2.set_ylabel('Send Out Quantity')
#
# plt.legend(loc='upper left')
# plt.grid(True)
# plt.show()

class StockChecker:
    def __init__(self, pycmc=None, start_date: date = date.today(), end_date: date = date.today() + timedelta(days=6)):
        self.pycommence = pycmc or PyCommence.with_csr(
            'Hire',
            filter_array=good_hires_in_range_array(start_date, end_date)
        )
        self.start_date = start_date
        self.end_date = end_date
        self.date_range_gen = daterang_gen(start_date, end_date)
        self.data = self._prepare_data()

    def _prepare_data(self):
        records = self.pycommence.records()
        df = pd.DataFrame(records)
        df[HireFields.SEND_OUT_DATE] = pd.to_datetime(df[HireFields.SEND_OUT_DATE], format=CmcDateFormat, errors='coerce')
        df[HireFields.DUE_BACK_DATE] = pd.to_datetime(df[HireFields.DUE_BACK_DATE], format=CmcDateFormat, errors='coerce')
        df[HireFields.UHF] = df[HireFields.UHF].astype(int)
        return df

    def run(self):
        dates = list(self.date_range_gen)
        send_data = [self.to_send(datecheck) for datecheck in dates]
        stock_data = [self.how_many_in(datecheck) for datecheck in dates]

        data_df = pd.DataFrame(
            {
                'Date': dates,
                'Send': send_data,
                'Stock': stock_data
            }
        )

        self.plot_data(data_df)

    def to_send(self, datecheck: date, radiotype=RadioType.HYT):
        filtered_data = self.data[
            (self.data[HireFields.SEND_OUT_DATE].dt.date == datecheck) &
            (self.data[HireFields.RADIO_TYPE] == radiotype)
            ]
        return filtered_data[HireFields.UHF].sum()

    def how_many_in(self, datecheck: date, radiotype=RadioType.HYT, stock: int = 500):
        filtered_data = self.data[
            (self.data[HireFields.SEND_OUT_DATE].dt.date < datecheck) &
            (self.data[HireFields.DUE_BACK_DATE].dt.date > datecheck) &
            (self.data[HireFields.RADIO_TYPE] == radiotype)
            ]
        rads_out = filtered_data[HireFields.UHF].sum()
        return stock - rads_out

    def plot_data(self, data_df):
        dates = data_df['Date']
        send = data_df['Send']
        radios_in = data_df['Stock']

        ax1 = plt.gca()
        ax2 = ax1.twinx()

        plt.figure(figsize=(14, 7))

        ax2.set_ylim(0, max(send) * 1.1)
        plt.sca(ax2)
        plt.bar(dates, send, width=0.4, color='blue', label='Send Quantity', alpha=0.7)

        plt.sca(ax1)
        plt.plot(dates, radios_in, label='Stock Level', color='green', marker='o')

        ax1.set_xticks(dates)
        ax1.set_xticklabels([datey.strftime('%a %d %b') for datey in dates], rotation=90, ha='right')

        ax1.xaxis.set_major_locator(mdates.DayLocator(interval=3))
        ax1.xaxis.set_major_formatter(mdates.ConciseDateFormatter(ax1.xaxis.get_major_locator()))
        plt.gcf().autofmt_xdate()

        ax1.set_xlabel('Date')
        ax1.set_ylabel('Stock Remaining')
        ax2.set_ylabel('Send Out Quantity')

        plt.legend(loc='upper left')
        plt.grid(True)
        plt.show()


if __name__ == '__main__':
    sc = StockChecker(
        start_date=date(2023, 4, 1),
        end_date=date(2023, 7, 1),
    )
    sc.run()
