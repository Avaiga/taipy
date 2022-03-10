from importlib import util

from taipy.gui import Gui
from taipy.gui.data.array_dict_data_accessor import _ArrayDictDataAccessor
from taipy.gui.data.data_format import _DataFormat

an_array = [1, 2, 3]


def test_simple_data(gui: Gui, helpers):
    accessor = _ArrayDictDataAccessor()
    ret_data = accessor.get_data(gui, "x", an_array, {"start": 0, "end": -1}, _DataFormat.JSON)
    assert ret_data
    value = ret_data["value"]
    assert value
    assert value["rowcount"] == 3
    data = value["data"]
    assert len(data) == 3


def test_simple_data_with_arrow(gui: Gui, helpers):
    if util.find_spec("pyarrow"):
        accessor = _ArrayDictDataAccessor()
        ret_data = accessor.get_data(gui, "x", an_array, {"start": 0, "end": -1}, _DataFormat.APACHE_ARROW)
        assert ret_data
        value = ret_data["value"]
        assert value
        assert value["rowcount"] == 3
        data = value["data"]
        assert isinstance(data, bytes)


def test_slice(gui: Gui, helpers):
    accessor = _ArrayDictDataAccessor()
    value = accessor.get_data(gui, "x", an_array, {"start": 0, "end": 1}, _DataFormat.JSON)["value"]
    assert value["rowcount"] == 3
    data = value["data"]
    assert len(data) == 2
    value = accessor.get_data(gui, "x", an_array, {"start": "0", "end": "1"}, _DataFormat.JSON)["value"]
    data = value["data"]
    assert len(data) == 2


def test_sort(gui: Gui, helpers):
    accessor = _ArrayDictDataAccessor()
    a_dict = {"name": ["A", "B", "C"], "value": [3, 2, 1]}
    query = {"columns": ["name", "value"], "start": 0, "end": -1, "orderby": "name", "sort": "desc"}
    data = accessor.get_data(gui, "x", a_dict, query, _DataFormat.JSON)["value"]["data"]
    assert data[0]["name"] == "C"


def test_aggregate(gui: Gui, helpers, small_dataframe):
    accessor = _ArrayDictDataAccessor()
    a_dict = {"name": ["A", "B", "C", "A"], "value": [3, 2, 1, 2]}
    query = {"columns": ["name", "value"], "start": 0, "end": -1, "aggregates": ["name"], "applies": {"value": "sum"}}
    value = accessor.get_data(gui, "x", a_dict, query, _DataFormat.JSON)["value"]
    assert value["rowcount"] == 3
    data = value["data"]
    assert {"name": "A", "value": 5} in data
