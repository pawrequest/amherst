import time
from datetime import date, timedelta

import pytest

from amherst.stockcheck import StockChecker, good_hires_in_range_array, hires_out_array, send_on_array
from pycommence.filters import FilterArray
from pycommence.pycommence_v1 import PyCommence

DATECHECK = date.today()


def pyc_hire_new():
    start_date = date(2023, 4, 1)
    end_date = date(2023, 7, 1)

    filter_array = good_hires_in_range_array(start_date, end_date)

    # pycmc = PyCommence.with_csr('paul hires', mode=CursorType.VIEW)
    pycmc = PyCommence.with_csr('Hire', filter_array=filter_array)
    if not pycmc.cmc_wrapper.delivery_contact_name == 'Radios':
        raise ValueError('Expected Radio DB')
    return pycmc


@pytest.fixture(scope='session', params=[pyc_hire_new])
def pyc_hire_prm(request):
    param = request.param
    return param()


def test_daterange():
    start_date = date.today()
    end_date = start_date + timedelta(days=3)
    # for i in daterang_gen(start_date, end_date):
    #     print(i)


def test_send_on_array():
    arr = send_on_array(DATECHECK)
    # print([fil for fil in arr.filters.values()])
    assert isinstance(arr, FilterArray)


def test_hires_out_array():
    arr = hires_out_array(DATECHECK)
    # print([fil for fil in arr.filters.values()])
    assert isinstance(arr, FilterArray)


def test_sc(pyc_hire_prm):
    starttime = time.perf_counter()
    sc = StockChecker(
        pycmc=pyc_hire_prm,
        start_date=date(2023, 4, 1),
        end_date=date(2023, 7, 1),
    )
    # data = sc.get_mat_data()
    endtime = time.perf_counter()
    print(f'THERE WERE {len(sc.data)} RECORDS')
    print(f'Elapsed time: {endtime - starttime}')
    assert sc
