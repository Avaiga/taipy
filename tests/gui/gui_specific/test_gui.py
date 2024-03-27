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
import json
from contextlib import nullcontext

import pandas as pd
import pytest

from taipy.gui import Gui
from taipy.gui.utils import _get_module_name_from_frame, _TaipyContent


def test__get_real_var_name(gui: Gui):
    res = gui._get_real_var_name("")
    frame = inspect.currentframe()
    gui._set_frame(frame)
    assert isinstance(res, tuple)
    assert res[0] == ""
    assert res[1] == ""

    gui.run(run_server=False)
    with gui.get_flask_app().app_context():
        with gui._set_locals_context(_get_module_name_from_frame(frame)) if frame else nullcontext():
            with pytest.raises(NameError):
                res = gui._get_real_var_name(f"{_TaipyContent.get_hash()}_var")


def test__get_user_instance(gui: Gui):
    gui.run(run_server=False)
    with gui.get_flask_app().app_context():
        with pytest.warns(UserWarning):
            gui._get_user_instance("", type(None))


def test__call_broadcast_callback(gui: Gui):
    gui.run(run_server=False)
    with gui.get_flask_app().app_context():
        res = gui._call_broadcast_callback(lambda s, t: t, ["Hello World"], "mine")
        assert res == "Hello World"

    with gui.get_flask_app().app_context():
        with pytest.warns(UserWarning):
            res = gui._call_broadcast_callback(print, ["Hello World"], "mine")
            assert res is None


def test__refresh_expr(gui: Gui):
    gui.run(run_server=False)
    with gui.get_flask_app().app_context():
        res = gui._refresh_expr("var", None)
        assert res is None


def test__tbl_cols(gui: Gui):
    data = pd.DataFrame({"col1": [0, 1, 2], "col2": [True, True, False]})
    gui.run(run_server=False)
    with gui.get_flask_app().app_context():
        res = gui._tbl_cols(True, None, json.dumps({}), json.dumps({"data": "data"}), data=data)
        assert isinstance(res, str)

        d = json.loads(res)
        assert isinstance(d, dict)
        assert d["col1"]["type"] == "int"

        res = gui._tbl_cols(False, None, "", "")
        assert repr(res) == "Taipy: Do not update"


def test__chart_conf(gui: Gui):
    data = pd.DataFrame({"col1": [0, 1, 2], "col2": [True, True, False]})
    gui.run(run_server=False)
    with gui.get_flask_app().app_context():
        res = gui._chart_conf(True, None, json.dumps({}), json.dumps({"data": "data"}), data=data)
        assert isinstance(res, str)

        d = json.loads(res)
        assert isinstance(d, dict)
        assert d["columns"]["col1"]["type"] == "int"

        res = gui._chart_conf(False, None, "", "")
        assert repr(res) == "Taipy: Do not update"

        with pytest.warns(UserWarning):
            res = gui._chart_conf(True, None, "", "")
            assert repr(res) == "Taipy: Do not update"


def test__get_valid_adapter_result(gui: Gui):
    gui.run(run_server=False)
    with gui.get_flask_app().app_context():
        res = gui._get_valid_adapter_result(("id", "label"))
        assert isinstance(res, tuple)
        assert res[0] == "id"
