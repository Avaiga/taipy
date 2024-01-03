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

import inspect
from datetime import datetime
from importlib import util
from unittest.mock import patch

import pandas  # type: ignore
from flask import g

from taipy.gui import Gui
from taipy.gui.data.data_format import _DataFormat
from taipy.gui.data.decimator import ScatterDecimator
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
    assert ret_data["alldata"] is True
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
    assert next(v.get("value") for v in data if v.get("name") == "A") == 5


def test_filters(gui: Gui, helpers, small_dataframe):
    accessor = _PandasDataAccessor()
    pd = pandas.DataFrame(data=small_dataframe)
    pd = pandas.concat(
        [pd, pandas.DataFrame(data={"name": ["A"], "value": [4]})], axis=0, join="outer", ignore_index=True
    )
    query = {
        "columns": ["name", "value"],
        "start": 0,
        "end": -1,
        "filters": [{"col": "name", "action": "!=", "value": ""}],
    }
    value = accessor.get_data(gui, "x", pd, query, _DataFormat.JSON)
    assert len(value["value"]["data"]) == 4

    query = {
        "columns": ["name", "value"],
        "start": 0,
        "end": -1,
        "filters": [{"col": "name", "action": "==", "value": ""}],
    }
    value = accessor.get_data(gui, "x", pd, query, _DataFormat.JSON)
    assert len(value["value"]["data"]) == 0

    query = {
        "columns": ["name", "value"],
        "start": 0,
        "end": -1,
        "filters": [{"col": "name", "action": "==", "value": "A"}],
    }
    value = accessor.get_data(gui, "x", pd, query, _DataFormat.JSON)
    assert len(value["value"]["data"]) == 2

    query = {
        "columns": ["name", "value"],
        "start": 0,
        "end": -1,
        "filters": [{"col": "name", "action": "==", "value": "A"}, {"col": "value", "action": "==", "value": 2}],
    }
    value = accessor.get_data(gui, "x", pd, query, _DataFormat.JSON)
    assert len(value["value"]["data"]) == 0

    query = {
        "columns": ["name", "value"],
        "start": 0,
        "end": -1,
        "filters": [{"col": "name", "action": "!=", "value": "A"}, {"col": "value", "action": "==", "value": 2}],
    }
    value = accessor.get_data(gui, "x", pd, query, _DataFormat.JSON)
    assert len(value["value"]["data"]) == 1
    assert value["value"]["data"][0]["_tp_index"] == 1


def test_filter_by_date(gui: Gui, helpers, small_dataframe):
    accessor = _PandasDataAccessor()
    pd = pandas.DataFrame(data=small_dataframe)
    pd["a date"] = [
        datetime.fromisocalendar(2022, 28, 1),
        datetime.fromisocalendar(2022, 28, 2),
        datetime.fromisocalendar(2022, 28, 3),
    ]
    query = {
        "columns": ["name", "value"],
        "start": 0,
        "end": -1,
        "filters": [{"col": "a date", "action": ">", "value": datetime.fromisocalendar(2022, 28, 3).isoformat() + "Z"}],
    }
    value = accessor.get_data(gui, "x", pd, query, _DataFormat.JSON)
    assert len(value["value"]["data"]) == 0
    query = {
        "columns": ["name", "value"],
        "start": 0,
        "end": -1,
        "filters": [{"col": "a date", "action": ">", "value": datetime.fromisocalendar(2022, 28, 2).isoformat() + "Z"}],
    }
    value = accessor.get_data(gui, "x", pd, query, _DataFormat.JSON)
    assert len(value["value"]["data"]) == 1
    query = {
        "columns": ["name", "value"],
        "start": 0,
        "end": -1,
        "filters": [{"col": "a date", "action": "<", "value": datetime.fromisocalendar(2022, 28, 3).isoformat() + "Z"}],
    }
    value = accessor.get_data(gui, "x", pd, query, _DataFormat.JSON)
    assert len(value["value"]["data"]) == 2
    query = {
        "columns": ["name", "value"],
        "start": 0,
        "end": -1,
        "filters": [
            {"col": "a date", "action": "<", "value": datetime.fromisocalendar(2022, 28, 2).isoformat() + "Z"},
            {"col": "a date", "action": ">", "value": datetime.fromisocalendar(2022, 28, 2).isoformat() + "Z"},
        ],
    }
    value = accessor.get_data(gui, "x", pd, query, _DataFormat.JSON)
    assert len(value["value"]["data"]) == 0
    query = {
        "columns": ["name", "value"],
        "start": 0,
        "end": -1,
        "filters": [
            {"col": "a date", "action": "<", "value": datetime.fromisocalendar(2022, 28, 3).isoformat() + "Z"},
            {"col": "a date", "action": ">", "value": datetime.fromisocalendar(2022, 28, 1).isoformat() + "Z"},
        ],
    }
    value = accessor.get_data(gui, "x", pd, query, _DataFormat.JSON)
    assert len(value["value"]["data"]) == 1


def test_decimator(gui: Gui, helpers, small_dataframe):
    a_decimator = ScatterDecimator()  # noqa: F841

    accessor = _PandasDataAccessor()
    pd = pandas.DataFrame(data=small_dataframe)

    # set gui frame
    if frame := inspect.currentframe():
        gui._set_frame(frame)

    gui.add_page("test", "<|Hello {a_decimator}|button|id={btn_id}|>")
    with patch("sys.argv", ["prog"]):
        gui.run(run_server=False)
    flask_client = gui._server.test_client()

    cid = helpers.create_scope_and_get_sid(gui)
    # Get the jsx once so that the page will be evaluated -> variable will be registered
    flask_client.get(f"/taipy-jsx/test?client_id={cid}")
    with gui.get_flask_app().test_request_context(f"/taipy-jsx/test/?client_id={cid}", data={"client_id": cid}):
        g.client_id = cid

        ret_data = accessor.get_data(
            gui,
            "x",
            pd,
            {
                "start": 0,
                "end": -1,
                "alldata": True,
                "decimatorPayload": {
                    "decimators": [{"decimator": "a_decimator", "chartMode": "markers"}],
                    "width": 100,
                },
            },
            _DataFormat.JSON,
        )
        assert ret_data
        value = ret_data["value"]
        assert value
        data = value["data"]
        assert len(data) == 2
