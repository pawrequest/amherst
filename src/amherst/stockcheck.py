from datetime import date, timedelta
from time import perf_counter
from typing import Generator

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from pawlogger import get_loguru

from amherst.commence import HireFields, HireStatus
from pycommence import PyCommence
from pycommence.pycmc_types import CmcFilter, ConditionType, FilterArray, RadioType, to_cmc_date
from pycommence.wrapper.cmc_db import CommenceWrapper

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


def send_on_date_fils(datecheck: date, radiotype=RadioType.HYT):
    return (
        CmcFilter(cmc_col=HireFields.SEND_OUT_DATE, condition=ConditionType.ON, value=to_cmc_date(datecheck)),
        CmcFilter(cmc_col=HireFields.RADIO_TYPE, condition=ConditionType.EQUAL, value=radiotype),
    )


def send_on_array(datecheck: date, radiotype=RadioType.HYT) -> FilterArray:
    fils = good_hires_fils() + send_on_date_fils(datecheck, radiotype)
    return FilterArray(filters={i: fil for i, fil in enumerate(fils, 1)})


def hires_out_array(datecheck: date, radiotype=RadioType.HYT):
    fils = good_hires_fils() + hires_out_fils(datecheck, radiotype)
    return FilterArray(filters={i: fil for i, fil in enumerate(fils, 1)})


def how_many_out(datecheck: date):
    out_filter = hires_out_array(datecheck)
    recs = get_records(out_filter)
    rads_out = sum([int(rec.get(HireFields.UHF)) for rec in recs])
    return rads_out


def how_many_in(datecheck: date, radiotype=RadioType.HYT, stock: int = 500):
    out_filter = hires_out_array(datecheck)
    recs = get_records(out_filter)
    rads_out = sum([int(rec.get(HireFields.UHF)) for rec in recs])
    return stock - rads_out


def to_send(datecheck: date, radiotype=RadioType.HYT):
    to_send_fil = send_on_array(datecheck, radiotype)
    recs = get_records(to_send_fil)
    res = sum([rads_in_rec(rec) for rec in recs])
    return res


def rads_in_rec(rec):
    return int(rec.get(HireFields.UHF))


def get_records(cmc_fil_array):
    with PyCommence.from_table_name_context('Hire', filter_array=cmc_fil_array) as pyc:
        recs = pyc.records()
    return recs


#
# def get_date_range(start_date, end_date):
#     return [start_date + timedelta(days=x) for x in range((end_date - start_date).days + 1)]


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


def do_matplot(start_date: date, end_date: date):
    dates_gen = daterang_gen(start_date, end_date)
    data = get_mat_data(dates_gen)

    dates = [d[0] for d in data]
    send = [d[1] for d in data]
    radios_in = [d[2] for d in data]
    # radios_out = [d[2] for d in data]

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


def get_mat_data(dates_gen):
    data = []
    start = perf_counter()
    for datecheck in dates_gen:
        print(f'Checking {datecheck.strftime("%a %d %b")}')
        send = to_send(datecheck)
        print(f'To Send: {send}')
        # rads_out = how_many_out(datecheck)
        rads_in = how_many_in(datecheck)
        print(f'Stock = {rads_in}')
        data.append((datecheck, send, rads_in))
    stop = perf_counter()
    print(f'Elapsed time: {stop - start} seconds')
    return data


def new_pycommence():
    wrapper = CommenceWrapper()
    csr = wrapper.get_cursor('Hire')


if __name__ == '__main__':
    do_matplot(date.today(), date.today() + timedelta(days=6))
