# Copyright 2022 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

from importlib import util

import pandas  # type: ignore

from taipy.gui import Gui
from taipy.gui.data.data_format import _DataFormat
from taipy.gui.data.pandas_data_accessor import _PandasDataAccessor


def test_simple_data(gui: Gui, helpers, small_dataframe):
    accessor = _PandasDataAccessor()
    pd = pandas.DataFrame(data=small_dataframe)
    ret_data = accessor.get_data(gui, "x", pd, {"start": 0, "end": -1}, _DataFormat.JSON)
    assert ret_data
    value = ret_data["value"]
    assert value
    assert value["rowcount"] == 3
    data = value["data"]
    assert len(data) == 3


def test_simple_data_with_arrow(gui: Gui, helpers, small_dataframe):
    if util.find_spec("pyarrow"):
        accessor = _PandasDataAccessor()
        pd = pandas.DataFrame(data=small_dataframe)
        ret_data = accessor.get_data(gui, "x", pd, {"start": 0, "end": -1}, _DataFormat.APACHE_ARROW)
        assert ret_data
        value = ret_data["value"]
        assert value
        assert value["rowcount"] == 3
        data = value["data"]
        assert isinstance(data, bytes)


def test_get_all_simple_data(gui: Gui, helpers, small_dataframe):
    accessor = _PandasDataAccessor()
    pd = pandas.DataFrame(data=small_dataframe)
    ret_data = accessor.get_data(gui, "x", pd, {"alldata": True}, _DataFormat.JSON)
    assert ret_data
    assert ret_data["alldata"] == True
    value = ret_data["value"]
    assert value
    data = value["data"]
    assert data == small_dataframe


def test_slice(gui: Gui, helpers, small_dataframe):
    accessor = _PandasDataAccessor()
    pd = pandas.DataFrame(data=small_dataframe)
    value = accessor.get_data(gui, "x", pd, {"start": 0, "end": 1}, _DataFormat.JSON)["value"]
    assert value["rowcount"] == 3
    data = value["data"]
    assert len(data) == 2
    value = accessor.get_data(gui, "x", pd, {"start": "0", "end": "1"}, _DataFormat.JSON)["value"]
    data = value["data"]
    assert len(data) == 2


def test_sort(gui: Gui, helpers, small_dataframe):
    accessor = _PandasDataAccessor()
    pd = pandas.DataFrame(data=small_dataframe)
    query = {"columns": ["name", "value"], "start": 0, "end": -1, "orderby": "name", "sort": "desc"}
    data = accessor.get_data(gui, "x", pd, query, _DataFormat.JSON)["value"]["data"]
    assert data[0]["name"] == "C"


def test_aggregate(gui: Gui, helpers, small_dataframe):
    accessor = _PandasDataAccessor()
    pd = pandas.DataFrame(data=small_dataframe)
    pd = pandas.concat(
        [pd, pandas.DataFrame(data={"name": ["A"], "value": [4]})], axis=0, join="outer", ignore_index=True
    )
    query = {"columns": ["name", "value"], "start": 0, "end": -1, "aggregates": ["name"], "applies": {"value": "sum"}}
    value = accessor.get_data(gui, "x", pd, query, _DataFormat.JSON)["value"]
    assert value["rowcount"] == 3
    data = value["data"]
    assert {"name": "A", "value": 5} in data
