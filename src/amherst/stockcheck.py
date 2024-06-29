from collections.abc import Generator
from datetime import date, timedelta

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from pawlogger import get_loguru

from amherst.commence import HireFields, HireStatus
from pycommence.pyc2 import PyCommence
from pycommence.pycmc_types import CmcFilter, ConditionType, FilterArray, RadioType, to_cmc_date

logger = get_loguru(profile='local')


def good_hires_fils():
    return (
        CmcFilter(cmc_col=HireFields.STATUS, condition=ConditionType.NOT_EQUAL, value=HireStatus.CANCELLED),
        CmcFilter(cmc_col=HireFields.STATUS, condition=ConditionType.NOT_EQUAL, value=HireStatus.RTN_OK),
        CmcFilter(cmc_col=HireFields.STATUS, condition=ConditionType.NOT_EQUAL, value=HireStatus.RTN_PROBLEMS),
    )


def hires_out_fils(datecheck: date, radiotype=RadioType.HYT):
    return (
        CmcFilter(cmc_col=HireFields.SEND_OUT_DATE, condition='Before', value=datecheck.isoformat()),
        CmcFilter(cmc_col=HireFields.DUE_BACK_DATE, condition='After', value=datecheck.isoformat()),
        CmcFilter(cmc_col=HireFields.RADIO_TYPE, condition='Equal To', value=radiotype),
    )


def good_hires_in_range_array(start_date: date, end_date: date, radiotype=RadioType.HYT):
    return FilterArray.from_filters(
        *good_hires_fils(),
        CmcFilter(cmc_col=HireFields.SEND_OUT_DATE, condition=ConditionType.BEFORE, value=to_cmc_date(end_date)),
        CmcFilter(cmc_col=HireFields.DUE_BACK_DATE, condition=ConditionType.AFTER, value=to_cmc_date(start_date)),
        CmcFilter(cmc_col=HireFields.RADIO_TYPE, condition=ConditionType.EQUAL, value=radiotype),
    )


def due_back_fil(datecheck):
    return CmcFilter(cmc_col=HireFields.DUE_BACK_DATE, condition=ConditionType.BEFORE, value=to_cmc_date(datecheck))


def due_out_fil(datecheck):
    return CmcFilter(cmc_col=HireFields.SEND_OUT_DATE, condition=ConditionType.BEFORE, value=to_cmc_date(datecheck))


def send_on_date_fils(datecheck: date, radiotype=RadioType.HYT):
    return (
        CmcFilter(cmc_col=HireFields.SEND_OUT_DATE, condition=ConditionType.ON, value=to_cmc_date(datecheck)),
        CmcFilter(cmc_col=HireFields.RADIO_TYPE, condition=ConditionType.EQUAL, value=radiotype),
    )


def send_on_array(datecheck: date, radiotype=RadioType.HYT) -> FilterArray:
    return FilterArray.from_filters(*good_hires_fils(), *send_on_date_fils(datecheck, radiotype))


def hires_out_array(datecheck: date, radiotype=RadioType.HYT):
    return FilterArray.from_filters(
        CmcFilter(cmc_col=HireFields.SEND_OUT_DATE, condition='Before', value=datecheck.isoformat()),
        CmcFilter(cmc_col=HireFields.DUE_BACK_DATE, condition='After', value=datecheck.isoformat()),
        CmcFilter(cmc_col=HireFields.RADIO_TYPE, condition='Equal To', value=radiotype),
        *good_hires_fils(),
    )


def rads_in_rec(rec):
    return int(rec.get(HireFields.UHF))


def daterang_gen(start_date, end_date) -> Generator[date, None, None]:
    for x in range((end_date - start_date).days + 1):
        thisdate = start_date + timedelta(days=x)
        yield thisdate


def custom_date_formatter(x, pos):
    datecheck = mdates.num2date(x)
    if datecheck.weekday() < 5:
        return
    if datecheck.day == 1:  # Check if the date is the first of a month
        return datecheck.strftime('%b %A %d')  # Month name and day
    else:
        return datecheck.strftime('%A %d')  # Just the day


class StockChecker:
    def __init__(self, pycmc=None, start_date: date = date.today(), end_date: date = date.today() + timedelta(days=6)):
        self.pycommence = pycmc or PyCommence.with_csr(
            'Hire',
            filter_array=good_hires_in_range_array(start_date, end_date)
        )
        self.start_date = start_date
        self.end_date = end_date
        self.date_range_gen = daterang_gen(start_date, end_date)
        self.data = self.pycommence.records()

    def to_send(self, datecheck: date, radiotype=RadioType.HYT):
        """How many radios to send on a given date"""
        to_send_fil = send_on_array(datecheck, radiotype)
        recs = self.get_records(to_send_fil)
        return sum([rads_in_rec(rec) for rec in recs])

    def how_many_in(self, datecheck: date, radiotype=RadioType.HYT, stock: int = 500):
        out_filter = hires_out_array(datecheck)
        recs = self.get_records(out_filter)
        rads_out = sum([int(rec.get(HireFields.UHF)) for rec in recs])
        return stock - rads_out

    def get_records(self, cmc_fil_array: FilterArray):
        with self.pycommence.temporary_filter_cursor(cmc_fil_array):
            recs = self.pycommence.records()
        return recs

    def get_mat_data(self):
        data = []
        for datecheck in self.date_range_gen:
            print(f'Checking {datecheck.strftime("%a %d %b")}')
            send = self.to_send(datecheck)
            print(f'To Send: {send}')
            rads_in = self.how_many_in(datecheck)
            print(f'Stock = {rads_in}')
            data.append((datecheck, send, rads_in))
        return data

    def run(self):
        data = self.get_mat_data()

        dates = [d[0] for d in data]
        send = [d[1] for d in data]
        radios_in = [d[2] for d in data]

        ax1 = plt.gca()
        ax2 = ax1.twinx()

        # Plotting the data
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
    sc = StockChecker()
    sc.run()
