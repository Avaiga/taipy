import pandas as pd
import pytest
from unittest.mock import Mock

from taipy.gui.data.pandas_data_accessor import _PandasDataAccessor

# Define a mock to simulate _DataFormat behavior with a 'value' attribute
class MockDataFormat:
    LIST = Mock(value="list")
    CSV = Mock(value="csv")

@pytest.fixture
def pandas_accessor():
    gui = Mock()  
    return _PandasDataAccessor(gui=gui)

@pytest.fixture
def sample_df():
    data = {
        "StringCol": ["Apple", "Banana", "Cherry", "apple"],
        "NumberCol": [10, 20, 30, 40],
        "BoolCol": [True, False, True, False],
        "DateCol": pd.to_datetime(["2020-01-01", "2021-06-15", "2022-08-22", "2023-03-05"])
    }
    return pd.DataFrame(data)

def test_contains_case_sensitive(pandas_accessor, sample_df):
    payload = {
        "filters": [{"col": "StringCol", "value": "Apple", "action": "contains", "matchCase": True}]
    }
    result = pandas_accessor.get_data("test_var", sample_df, payload, MockDataFormat.LIST)
    filtered_data = pd.DataFrame(result['value']['data'])
    
    assert len(filtered_data) == 1
    assert filtered_data.iloc[0]['StringCol'] == 'Apple'

def test_contains_case_insensitive(pandas_accessor, sample_df):
    payload = {
        "filters": [{"col": "StringCol", "value": "apple", "action": "contains", "matchCase": False}]
    }
    result = pandas_accessor.get_data("test_var", sample_df, payload, MockDataFormat.LIST)
    filtered_data = pd.DataFrame(result['value']['data'])
    
    assert len(filtered_data) == 2
    assert 'Apple' in filtered_data['StringCol'].values
    assert 'apple' in filtered_data['StringCol'].values

def test_numeric_filter(pandas_accessor, sample_df):
    payload = {
        "filters": [{"col": "NumberCol", "value": 20, "action": "=="}]
    }
    result = pandas_accessor.get_data("test_var", sample_df, payload, MockDataFormat.LIST)
    filtered_data = pd.DataFrame(result['value']['data'])
    
    assert len(filtered_data) == 1
    assert filtered_data.iloc[0]['NumberCol'] == 20

def test_boolean_filter(pandas_accessor, sample_df):
    payload = {
        "filters": [{"col": "BoolCol", "value": True, "action": "=="}]
    }
    result = pandas_accessor.get_data("test_var", sample_df, payload, MockDataFormat.LIST)
    filtered_data = pd.DataFrame(result['value']['data'])
    
    assert len(filtered_data) == 2
    assert all(filtered_data['BoolCol'])

def test_date_filter(pandas_accessor, sample_df):
    payload = {
        "filters": [{"col": "DateCol", "value": "2021-06-15", "action": "=="}]
    }
    result = pandas_accessor.get_data("test_var", sample_df, payload, MockDataFormat.LIST)
    filtered_data = pd.DataFrame(result['value']['data'])
    
    assert len(filtered_data) == 1
    assert filtered_data.iloc[0]['DateCol_str'] == "2021-06-14T18:30:00.000000Z"  
