from datetime import date, timedelta
from pprint import pprint

from amherst.stockcheck import daterang_gen, hires_out_array, send_on_array
from pycommence import FilterArray

DATECHECK = date.today()


def test_daterange():
    start_date = date.today()
    end_date = start_date + timedelta(days=3)
    for i in daterang_gen(start_date, end_date):
        print(i)


def test_send_on_array():
    arr = send_on_array(DATECHECK)
    pprint(arr.filters)
    assert isinstance(arr, FilterArray)


def test_hires_out_array():
    arr = hires_out_array(DATECHECK)
    pprint(arr.filters)
    assert isinstance(arr, FilterArray)
