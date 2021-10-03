#!/usr/bin/env python
import pytest
from pytest import raises
import json
from pathlib import Path
from process_covid import (load_covid_data,
                           cases_per_population_by_age,
                           hospital_vs_confirmed,
                           create_confirmed_plot,
                           count_high_rain_low_tests_days,
                           rebin,
                           compute_running_average)

data_directory = Path('covid_data')
data_file = "ER-Mi-EV_2020-03-16_2020-04-24.json"


# Negative test that checks load_covid_data throws a meaningful error
def test_negative_load_covid_data():
    # Test a file from public data release
    with raises(NotImplementedError) as e:
        data_file_test = "ER-Mi-EV_2020-03-16_2020-04-24.json"
        load_covid_data(data_directory / data_file_test)

# Test rebin with data given by examples
def test_rebin():
    data_er = load_covid_data(data_directory / data_file)
    t_data = data_er
    inputValidBinA = ['0-9','10-19','20-29','30-39','40-49','50-']
    inputValidBinB = ['0-19','20-39','40-']
    inputInValidBinA = ['0-14','15-29','30-44','45-']
    inputInvalidBinB = ['0-19','20-39','40-']
    expected_rebin_valid = ['0-19','20-39','40-']
    actual_rebin_valid = rebin(inputValidBinA,inputValidBinB)
    assert (expected_rebin_valid) == (actual_rebin_valid)

    with raises(NotImplementedError) as e:
        actual_rebin_invalid = rebin(inputInValidBinA, inputInvalidBinB)
        assert e.match("Error for rebin")
        
# test hospital_vs_confirmed with missing data
def test_hospital_vs_confirmed():
    data_er = load_covid_data(data_directory / data_file)
    t_data = data_er
    # Data from jim.pynb
    date = list(t_data["evolution"].keys())[0]
    t_data["evolution"][date]["hospitalizations"]["hospitalized"]["new"]["all"] = None
    t_data["evolution"][date]["epidemiology"]["confirmed"]["new"]["all"] = None
    expected_date=["2020-03-17","2020-03-18","2020-03-19","2020-03-20","2020-03-21"]
    expected_ratio=[0.2, 0.25, 0.14, 0.5, 0.33]
    t_date, t_ratio = hospital_vs_confirmed(t_data)
    actual_date=t_date[0:5]
    actual_ratio=[round(i,2) for i in t_ratio[0:5]]
    assert (expected_date,expected_ratio) == (actual_date,actual_ratio)


# One or multiple (parameterised) tests of compute_running_average check windows of different sizes
def test_compute_running_average():
    data_er = load_covid_data(data_directory / data_file)
    t_data = data_er
    t_date = t_data["evolution"].keys()
    odd_window = 3
    even_window = 2
    # Test data from example
    t_data1 = [0,1,5,2,2,5]
    t_data2 = [2, None, 4]
    expected_odd = [None, 2.0, 2.0, 2.0, 2.0, None]
    actual_odd = compute_running_average(t_data1,odd_window)
    assert (expected_odd) == (actual_odd)
    # Raise error when window size is even
    with raises(NotImplementedError) as e:
        actual_even = compute_running_average(t_data2,even_window)
        assert e.match('Window size should be odd')