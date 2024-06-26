from datetime import date, timedelta

from matplotlib import pyplot as plt

from amherst.stockcheck import (
    daterang_gen,
    do_matplot,
    get_data,
    get_date_range,
    good_hires_fils,
    hires_out_array,
    hires_out_fils,
    how_many_out,
    rads_in_rec,
    send_on_array,
    send_on_date_fils,
    to_send,
)

from amherst.commence import HireFields
from pycommence.pycmc_types import CmcFilter, FilterArray


def test_good_hires_fils():
    result = good_hires_fils()
    assert len(result) == 3
    assert all(isinstance(fil, CmcFilter) for fil in result)


def test_hires_out_fils():
    datecheck = date.today()
    result = hires_out_fils(datecheck)
    assert len(result) == 3
    assert all(isinstance(fil, CmcFilter) for fil in result)


def test_send_on_date_fils():
    datecheck = date.today()
    result = send_on_date_fils(datecheck)
    assert len(result) == 2
    assert all(isinstance(fil, CmcFilter) for fil in result)


def test_send_on_array():
    datecheck = date.today()
    result = send_on_array(datecheck)
    assert isinstance(result, FilterArray)


def test_hires_out_array():
    datecheck = date.today()
    result = hires_out_array(datecheck)
    assert isinstance(result, FilterArray)


def test_how_many(mocker):
    mocker.patch('amherst.stockcheck.get_records', return_value=[{HireFields.UHF: '5'}, {HireFields.UHF: '10'}])
    datecheck = date.today()
    result = how_many_out(datecheck)
    assert result == 15


def test_to_send(mocker):
    mocker.patch('amherst.stockcheck.get_records', return_value=[{HireFields.UHF: '5'}, {HireFields.UHF: '10'}])
    datecheck = date.today()
    result = to_send(datecheck)
    assert result == 15


def test_rads_in_rec():
    rec = {HireFields.UHF: '5'}
    result = rads_in_rec(rec)
    assert result == 5


def test_get_data(mocker):
    mocker.patch('amherst.stockcheck.get_records', return_value=[{HireFields.UHF: '5'}, {HireFields.UHF: '10'}])
    start_date = date.today()
    end_date = start_date + timedelta(days=3)
    result = get_data(start_date, end_date)
    assert len(result) == 4


def test_get_date_range():
    start_date = date.today()
    end_date = start_date + timedelta(days=3)
    result = get_date_range(start_date, end_date)
    assert len(result) == 4


def test_daterang_gen():
    start_date = date.today()
    end_date = start_date + timedelta(days=3)
    result = list(daterang_gen(start_date, end_date))
    assert len(result) == 4


def test_do_matplot(mocker):
    mock_show = mocker.patch('matplotlib.pyplot.show')
    start_date = date.today()
    end_date = start_date + timedelta(days=3)
    do_matplot(start_date, end_date)
    mock_show.assert_called_once()
