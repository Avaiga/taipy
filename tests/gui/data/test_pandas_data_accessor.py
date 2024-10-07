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
import os
from datetime import datetime
from importlib import util

import pandas
from flask import g

from taipy.gui import Gui
from taipy.gui.data.data_format import _DataFormat
from taipy.gui.data.decimator import ScatterDecimator
from taipy.gui.data.pandas_data_accessor import _PandasDataAccessor


def test_simple_data(gui: Gui, helpers, small_dataframe):
    accessor = _PandasDataAccessor(gui)
    pd = pandas.DataFrame(data=small_dataframe)
    ret_data = accessor.get_data("x", pd, {"start": 0, "end": -1}, _DataFormat.JSON)
    assert ret_data
    value = ret_data["value"]
    assert value
    assert value["rowcount"] == 3
    data = value["data"]
    assert len(data) == 3


def test_simple_data_with_arrow(gui: Gui, helpers, small_dataframe):
    if util.find_spec("pyarrow"):
        accessor = _PandasDataAccessor(gui)
        pd = pandas.DataFrame(data=small_dataframe)
        ret_data = accessor.get_data("x", pd, {"start": 0, "end": -1}, _DataFormat.APACHE_ARROW)
        assert ret_data
        value = ret_data["value"]
        assert value
        assert value["rowcount"] == 3
        data = value["data"]
        assert isinstance(data, bytes)


def test_get_all_simple_data(gui: Gui, helpers, small_dataframe):
    accessor = _PandasDataAccessor(gui)
    pd = pandas.DataFrame(data=small_dataframe)
    ret_data = accessor.get_data("x", pd, {"alldata": True}, _DataFormat.JSON)
    assert ret_data
    assert ret_data["alldata"] is True
    value = ret_data["value"]
    assert value
    data = value["data"]
    assert data == small_dataframe


def test_slice(gui: Gui, helpers, small_dataframe):
    accessor = _PandasDataAccessor(gui)
    pd = pandas.DataFrame(data=small_dataframe)
    value = accessor.get_data("x", pd, {"start": 0, "end": 1}, _DataFormat.JSON)["value"]
    assert value["rowcount"] == 3
    data = value["data"]
    assert len(data) == 2
    value = accessor.get_data("x", pd, {"start": "0", "end": "1"}, _DataFormat.JSON)["value"]
    data = value["data"]
    assert len(data) == 2


def test_style(gui: Gui, helpers, small_dataframe):
    accessor = _PandasDataAccessor(gui)
    pd = pandas.DataFrame(data=small_dataframe)
    gui.run(run_server=False)
    cid = helpers.create_scope_and_get_sid(gui)
    with gui.get_flask_app().test_request_context(f"/taipy-jsx/test/?client_id={cid}", data={"client_id": cid}):
        g.client_id = cid
        value = accessor.get_data("x", pd, {"start": 0, "end": 1, "styles": {"st": "test_style"}}, _DataFormat.JSON)[
            "value"
        ]
        assert value["rowcount"] == 3
        data = value["data"]
        assert len(data) == 2
        assert "test_style" in data[0]


def test_tooltip(gui: Gui, helpers, small_dataframe):
    def tt(state, value, index: int, row, column_name: str):
        return f"{column_name}[{index}]: {value}"

    accessor = _PandasDataAccessor(gui)
    pd = pandas.DataFrame(data=small_dataframe)
    gui.run(run_server=False)
    cid = helpers.create_scope_and_get_sid(gui)
    with gui.get_flask_app().test_request_context(f"/taipy-jsx/test/?client_id={cid}", data={"client_id": cid}):
        gui._bind_var_val("tt", tt)
        gui._get_locals_bind_from_context(None)["tt"] = tt
        g.client_id = cid
        value = accessor.get_data("x", pd, {"start": 0, "end": 1, "tooltips": {"tt": "tt"}}, _DataFormat.JSON)["value"]
        assert value["rowcount"] == 3
        data = value["data"]
        assert len(data) == 2
        assert "tt" in data[0]


def test_format_fn(gui: Gui, helpers, small_dataframe):
    def ff(state, value, index: int, row, column_name: str):
        return f"{column_name}[{index}]: {value}"

    accessor = _PandasDataAccessor(gui)
    pd = pandas.DataFrame(data=small_dataframe)
    gui.run(run_server=False)
    cid = helpers.create_scope_and_get_sid(gui)
    with gui.get_flask_app().test_request_context(f"/taipy-jsx/test/?client_id={cid}", data={"client_id": cid}):
        gui._bind_var_val("ff", ff)
        gui._get_locals_bind_from_context(None)["ff"] = ff
        g.client_id = cid
        value = accessor.get_data("x", pd, {"start": 0, "end": 1, "formats": {"ff": "ff"}}, _DataFormat.JSON)["value"]
        assert value["rowcount"] == 3
        data = value["data"]
        assert len(data) == 2
        assert "ff" in data[0]


def test_sort(gui: Gui, helpers, small_dataframe):
    accessor = _PandasDataAccessor(gui)
    pd = pandas.DataFrame(data=small_dataframe)
    query = {"columns": ["name", "value"], "start": 0, "end": -1, "orderby": "name", "sort": "desc"}
    data = accessor.get_data("x", pd, query, _DataFormat.JSON)["value"]["data"]
    assert data[0]["name"] == "C"


def test_aggregate(gui: Gui, helpers, small_dataframe):
    accessor = _PandasDataAccessor(gui)
    pd = pandas.DataFrame(data=small_dataframe)
    pd = pandas.concat(
        [pd, pandas.DataFrame(data={"name": ["A"], "value": [4]})], axis=0, join="outer", ignore_index=True
    )
    query = {"columns": ["name", "value"], "start": 0, "end": -1, "aggregates": ["name"], "applies": {"value": "sum"}}
    value = accessor.get_data("x", pd, query, _DataFormat.JSON)["value"]
    assert value["rowcount"] == 3
    data = value["data"]
    assert next(v.get("value") for v in data if v.get("name") == "A") == 5


def test_filters(gui: Gui, helpers, small_dataframe):
    accessor = _PandasDataAccessor(gui)
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
    value = accessor.get_data("x", pd, query, _DataFormat.JSON)
    assert len(value["value"]["data"]) == 4

    query = {
        "columns": ["name", "value"],
        "start": 0,
        "end": -1,
        "filters": [{"col": "name", "action": "==", "value": ""}],
    }
    value = accessor.get_data("x", pd, query, _DataFormat.JSON)
    assert len(value["value"]["data"]) == 0

    query = {
        "columns": ["name", "value"],
        "start": 0,
        "end": -1,
        "filters": [{"col": "name", "action": "==", "value": "A"}],
    }
    value = accessor.get_data("x", pd, query, _DataFormat.JSON)
    assert len(value["value"]["data"]) == 2

    query = {
        "columns": ["name", "value"],
        "start": 0,
        "end": -1,
        "filters": [{"col": "name", "action": "==", "value": "A"}, {"col": "value", "action": "==", "value": 2}],
    }
    value = accessor.get_data("x", pd, query, _DataFormat.JSON)
    assert len(value["value"]["data"]) == 0

    query = {
        "columns": ["name", "value"],
        "start": 0,
        "end": -1,
        "filters": [{"col": "name", "action": "!=", "value": "A"}, {"col": "value", "action": "==", "value": 2}],
    }
    value = accessor.get_data("x", pd, query, _DataFormat.JSON)
    assert len(value["value"]["data"]) == 1
    assert value["value"]["data"][0]["_tp_index"] == 1


def test_filter_by_date(gui: Gui, helpers, small_dataframe):
    accessor = _PandasDataAccessor(gui)
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
    value = accessor.get_data("x", pd, query, _DataFormat.JSON)
    assert len(value["value"]["data"]) == 0
    query = {
        "columns": ["name", "value"],
        "start": 0,
        "end": -1,
        "filters": [{"col": "a date", "action": ">", "value": datetime.fromisocalendar(2022, 28, 2).isoformat() + "Z"}],
    }
    value = accessor.get_data("x", pd, query, _DataFormat.JSON)
    assert len(value["value"]["data"]) == 1
    query = {
        "columns": ["name", "value"],
        "start": 0,
        "end": -1,
        "filters": [{"col": "a date", "action": "<", "value": datetime.fromisocalendar(2022, 28, 3).isoformat() + "Z"}],
    }
    value = accessor.get_data("x", pd, query, _DataFormat.JSON)
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
    value = accessor.get_data("x", pd, query, _DataFormat.JSON)
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
    value = accessor.get_data("x", pd, query, _DataFormat.JSON)
    assert len(value["value"]["data"]) == 1


def test_decimator(gui: Gui, helpers, small_dataframe):
    a_decimator = ScatterDecimator(threshold=1)  # noqa: F841

    accessor = _PandasDataAccessor(gui)
    pd = pandas.DataFrame(data=small_dataframe)

    # set gui frame
    gui._set_frame(inspect.currentframe())

    gui.add_page("test", "<|Hello {a_decimator}|button|>")
    gui.run(run_server=False)
    flask_client = gui._server.test_client()

    cid = helpers.create_scope_and_get_sid(gui)
    # Get the jsx once so that the page will be evaluated -> variable will be registered
    flask_client.get(f"/taipy-jsx/test?client_id={cid}")
    with gui.get_flask_app().test_request_context(f"/taipy-jsx/test/?client_id={cid}", data={"client_id": cid}):
        g.client_id = cid

        ret_data = accessor.get_data(
            "x",
            pd,
            {
                "start": 0,
                "end": -1,
                "alldata": True,
                "decimatorPayload": {
                    "decimators": [
                        {"decimator": "a_decimator", "chartMode": "markers", "xAxis": "name", "yAxis": "value"}
                    ],
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


def test_edit(gui, small_dataframe):
    accessor = _PandasDataAccessor(gui)
    pd = pandas.DataFrame(small_dataframe)
    ln = len(pd)
    assert pd["value"].iloc[0] != 10
    ret_data = accessor.on_edit(pd, {"index": 0, "col": "value", "value": 10})
    assert isinstance(ret_data, pandas.DataFrame)
    assert len(ret_data) == ln
    assert ret_data["value"].iloc[0] == 10


def test_delete(gui, small_dataframe):
    accessor = _PandasDataAccessor(gui)
    pd = pandas.DataFrame(small_dataframe)
    ln = len(pd)
    ret_data = accessor.on_delete(pd, {"index": 0})
    assert isinstance(ret_data, pandas.DataFrame)
    assert len(ret_data) == ln - 1


def test_add(gui, small_dataframe):
    accessor = _PandasDataAccessor(gui)
    pd = pandas.DataFrame(small_dataframe)
    ln = len(pd)

    ret_data = accessor.on_add(pd, {"index": 0})
    assert isinstance(ret_data, pandas.DataFrame)
    assert len(ret_data) == ln + 1
    assert ret_data["value"].iloc[0] == 0
    assert ret_data["name"].iloc[0] == ""

    ret_data = accessor.on_add(pd, {"index": 2})
    assert isinstance(ret_data, pandas.DataFrame)
    assert len(ret_data) == ln + 1
    assert ret_data["value"].iloc[2] == 0
    assert ret_data["name"].iloc[2] == ""

    ret_data = accessor.on_add(pd, {"index": 0}, ["New", 100])
    assert isinstance(ret_data, pandas.DataFrame)
    assert len(ret_data) == ln + 1
    assert ret_data["value"].iloc[0] == 100
    assert ret_data["name"].iloc[0] == "New"

    ret_data = accessor.on_add(pd, {"index": 2}, ["New", 100])
    assert isinstance(ret_data, pandas.DataFrame)
    assert len(ret_data) == ln + 1
    assert ret_data["value"].iloc[2] == 100
    assert ret_data["name"].iloc[2] == "New"


def test_csv(gui, small_dataframe):
    accessor = _PandasDataAccessor(gui)
    pd = pandas.DataFrame(small_dataframe)
    path = accessor.to_csv("", pd)
    assert path is not None
    assert os.path.getsize(path) > 0
