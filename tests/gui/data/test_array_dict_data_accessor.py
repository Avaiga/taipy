# Copyright 2021-2024 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import os
from importlib import util

from taipy.gui import Gui
from taipy.gui.data.array_dict_data_accessor import _ArrayDictDataAccessor
from taipy.gui.data.data_format import _DataFormat
from taipy.gui.utils import _MapDict

an_array = [1, 2, 3]


def test_simple_data(gui: Gui, helpers):
    accessor = _ArrayDictDataAccessor(gui)
    ret_data = accessor.get_data("x", an_array, {"start": 0, "end": -1}, _DataFormat.JSON)
    assert ret_data
    value = ret_data["value"]
    assert value
    assert value["rowcount"] == 3
    data = value["data"]
    assert len(data) == 3


def test_simple_data_with_arrow(gui: Gui, helpers):
    if util.find_spec("pyarrow"):
        accessor = _ArrayDictDataAccessor(gui)
        ret_data = accessor.get_data("x", an_array, {"start": 0, "end": -1}, _DataFormat.APACHE_ARROW)
        assert ret_data
        value = ret_data["value"]
        assert value
        assert value["rowcount"] == 3
        data = value["data"]
        assert isinstance(data, bytes)


def test_slice(gui: Gui, helpers):
    accessor = _ArrayDictDataAccessor(gui)
    value = accessor.get_data("x", an_array, {"start": 0, "end": 1}, _DataFormat.JSON)["value"]
    assert value["rowcount"] == 3
    data = value["data"]
    assert len(data) == 2
    value = accessor.get_data("x", an_array, {"start": "0", "end": "1"}, _DataFormat.JSON)["value"]
    data = value["data"]
    assert len(data) == 2


def test_sort(gui: Gui, helpers):
    accessor = _ArrayDictDataAccessor(gui)
    a_dict = {"name": ["A", "B", "C"], "value": [3, 2, 1]}
    query = {"columns": ["name", "value"], "start": 0, "end": -1, "orderby": "name", "sort": "desc"}
    data = accessor.get_data("x", a_dict, query, _DataFormat.JSON)["value"]["data"]
    assert data[0]["name"] == "C"


def test_aggregate(gui: Gui, helpers, small_dataframe):
    accessor = _ArrayDictDataAccessor(gui)
    a_dict = {"name": ["A", "B", "C", "A"], "value": [3, 2, 1, 2]}
    query = {"columns": ["name", "value"], "start": 0, "end": -1, "aggregates": ["name"], "applies": {"value": "sum"}}
    value = accessor.get_data("x", a_dict, query, _DataFormat.JSON)["value"]
    assert value["rowcount"] == 3
    data = value["data"]
    agregValue = next(v.get("value") for v in data if v.get("name") == "A")
    assert agregValue == 5


def test_array_of_array(gui: Gui, helpers, small_dataframe):
    accessor = _ArrayDictDataAccessor(gui)
    an_array = [[1, 2, 3], [2, 4, 6]]
    ret_data = accessor.get_data("x", an_array, {"start": 0, "end": -1}, _DataFormat.JSON)
    assert ret_data
    value = ret_data["value"]
    assert value
    assert value["rowcount"] == 2
    data = value["data"]
    assert len(data) == 2
    assert len(data[0]) == 4  # including _tp_index


def test_empty_array(gui: Gui, helpers, small_dataframe):
    accessor = _ArrayDictDataAccessor(gui)
    an_array: list[str] = []
    ret_data = accessor.get_data("x", an_array, {"start": 0, "end": -1}, _DataFormat.JSON)
    assert ret_data
    value = ret_data["value"]
    assert value
    assert value["rowcount"] == 0
    data = value["data"]
    assert len(data) == 0


def test_array_of_diff_array(gui: Gui, helpers, small_dataframe):
    accessor = _ArrayDictDataAccessor(gui)
    an_array = [[1, 2, 3], [2, 4]]
    ret_data = accessor.get_data("x", an_array, {"start": 0, "end": -1, "alldata": True}, _DataFormat.JSON)
    assert ret_data
    value = ret_data["value"]
    assert value
    assert value["multi"] is True
    data = value["data"]
    assert len(data) == 2
    assert len(data[0]["0/0"]) == 3
    assert len(data[1]["1/0"]) == 2


def test_array_of_dicts(gui: Gui, helpers, small_dataframe):
    accessor = _ArrayDictDataAccessor(gui)
    an_array_of_dicts = [
        {
            "temperatures": [
                [17.2, 27.4, 28.6, 21.5],
                [5.6, 15.1, 20.2, 8.1],
                [26.6, 22.8, 21.8, 24.0],
                [22.3, 15.5, 13.4, 19.6],
                [3.9, 18.9, 25.7, 9.8],
            ],
            "cities": ["Hanoi", "Paris", "Rio de Janeiro", "Sydney", "Washington"],
        },
        {"seasons": ["Winter", "Summer", "Spring", "Autumn"]},
    ]
    ret_data = accessor.get_data("x", an_array_of_dicts, {"start": 0, "end": -1, "alldata": True}, _DataFormat.JSON)
    assert ret_data
    value = ret_data["value"]
    assert value
    assert value["multi"] is True
    data = value["data"]
    assert len(data) == 2
    assert len(data[0]["temperatures"]) == 5
    assert len(data[1]["seasons"]) == 4


def test_array_of_Mapdicts(gui: Gui, helpers, small_dataframe):
    accessor = _ArrayDictDataAccessor(gui)
    dict1 = _MapDict(
        {
            "temperatures": [
                [17.2, 27.4, 28.6, 21.5],
                [5.6, 15.1, 20.2, 8.1],
                [26.6, 22.8, 21.8, 24.0],
                [22.3, 15.5, 13.4, 19.6],
                [3.9, 18.9, 25.7, 9.8],
            ],
            "cities": ["Hanoi", "Paris", "Rio de Janeiro", "Sydney", "Washington"],
        }
    )
    dict2 = _MapDict({"seasons": ["Winter", "Summer", "Spring", "Autumn"]})
    ret_data = accessor.get_data("x", [dict1, dict2], {"start": 0, "end": -1, "alldata": True}, _DataFormat.JSON)
    assert ret_data
    value = ret_data["value"]
    assert value
    assert value["multi"] is True
    data = value["data"]
    assert len(data) == 2
    assert len(data[0]["temperatures"]) == 5
    assert len(data[1]["seasons"]) == 4


def test_edit_dict(gui, small_dataframe):
    accessor = _ArrayDictDataAccessor(gui)
    pd = small_dataframe
    ln = len(pd["name"])
    assert pd["value"][0] != 10
    ret_data = accessor.on_edit(pd, {"index": 0, "col": "value", "value": 10})
    assert isinstance(ret_data, dict)
    assert len(ret_data["name"]) == ln
    assert ret_data["value"][0] == 10


def test_delete_dict(gui, small_dataframe):
    accessor = _ArrayDictDataAccessor(gui)
    pd = small_dataframe
    ln = len(pd['name'])
    ret_data = accessor.on_delete(pd, {"index": 0})
    assert isinstance(ret_data, dict)
    assert len(ret_data["name"]) == ln - 1


def test_add_dict(gui, small_dataframe):
    accessor = _ArrayDictDataAccessor(gui)
    pd = small_dataframe
    ln = len(pd["name"])

    ret_data = accessor.on_add(pd, {"index": 0})
    assert isinstance(ret_data, dict)
    assert len(ret_data["name"]) == ln + 1
    assert ret_data["value"][0] == 0
    assert ret_data["name"][0] == ""

    ret_data = accessor.on_add(pd, {"index": 2})
    assert isinstance(ret_data, dict)
    assert len(ret_data["name"]) == ln + 1
    assert ret_data["value"][2] == 0
    assert ret_data["name"][2] == ""

    ret_data = accessor.on_add(pd, {"index": 0}, ["New", 100])
    assert isinstance(ret_data, dict)
    assert len(ret_data["name"]) == ln + 1
    assert ret_data["value"][0] == 100
    assert ret_data["name"][0] == "New"

    ret_data = accessor.on_add(pd, {"index": 2}, ["New", 100])
    assert isinstance(ret_data, dict)
    assert len(ret_data["name"]) == ln + 1
    assert ret_data["value"][2] == 100
    assert ret_data["name"][2] == "New"


def test_csv(gui, small_dataframe):
    accessor = _ArrayDictDataAccessor(gui)
    pd = small_dataframe
    path = accessor.to_csv("", pd)
    assert path is not None
    assert os.path.getsize(path) > 0
