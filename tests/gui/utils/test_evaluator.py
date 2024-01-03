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
import warnings
from unittest.mock import patch

from flask import g

from taipy.gui import Gui
from taipy.gui.utils.types import _TaipyNumber


def test_unbind_variable_in_expression(gui: Gui, helpers):
    with patch("sys.argv", ["prog"]):
        gui.run(run_server=False, single_client=True)
    with warnings.catch_warnings(record=True) as records:
        with gui.get_flask_app().app_context():
            gui._evaluate_expr("{x}")
            warns = helpers.get_taipy_warnings(records)
            assert len(warns) == 3
            assert "Variable 'x' is not available in" in str(warns[0].message)
            assert "Variable 'x' is not defined" in str(warns[1].message)
            assert "Cannot evaluate expression 'x'" in str(warns[2].message)
            assert "name 'x' is not defined" in str(warns[2].message)


def test_evaluate_same_expression_multiple_times(gui: Gui):
    x = 10  # noqa: F841
    if frame := inspect.currentframe():
        gui._set_frame(frame)
    with patch("sys.argv", ["prog"]):
        gui.run(run_server=False, single_client=True)
    with gui.get_flask_app().app_context():
        s1 = gui._evaluate_expr("x + 10 = {x + 10}")
        s2 = gui._evaluate_expr("x + 10 = {x + 10}")
        assert s1 == s2


def test_evaluate_expressions_same_variable(gui: Gui):
    x = 10  # noqa: F841
    if frame := inspect.currentframe():
        gui._set_frame(frame)
    with patch("sys.argv", ["prog"]):
        gui.run(run_server=False, single_client=True)
    with gui.get_flask_app().app_context():
        s1 = gui._evaluate_expr("x + 10 = {x + 10}")
        s2 = gui._evaluate_expr("x = {x}")
        assert "tp_TpExPr_x" in s1 and "tp_TpExPr_x" in s2


def test_evaluate_holder(gui: Gui):
    x = 10  # noqa: F841
    if frame := inspect.currentframe():
        gui._set_frame(frame)
    with patch("sys.argv", ["prog"]):
        gui.run(run_server=False, single_client=True)
    with warnings.catch_warnings(record=True):
        with gui.get_flask_app().app_context():
            gui._evaluate_expr("{x + 10}")
            hash = gui._evaluate_bind_holder(_TaipyNumber, "TpExPr_x + 10_TPMDL_0")
            assert "_TpN_tp_TpExPr_x_10_TPMDL_0_0" in hash
            lst = gui._evaluate_holders("TpExPr_x + 10_TPMDL_0")
            assert len(lst) == 1
            assert "_TpN_tp_TpExPr_x_10_TPMDL_0_0" in lst[0]
            # test re-evaluate holders
            gui._bindings().x = 20
            gui._re_evaluate_expr(lst[0])


def test_evaluate_not_expression_type(gui: Gui):
    with patch("sys.argv", ["prog"]):
        gui.run(run_server=False)
    with gui.get_flask_app().app_context():
        assert "x + 10" == gui._evaluate_expr("x + 10")


def test_evaluate_expression_2_clients(gui: Gui):
    x = 10  # noqa: F841
    y = 20  # noqa: F841
    if frame := inspect.currentframe():
        gui._set_frame(frame)
    with patch("sys.argv", ["prog"]):
        gui.run(run_server=False)
    with gui.get_flask_app().app_context():
        gui._bindings()._get_or_create_scope("A")
        gui._bindings()._get_or_create_scope("B")
        g.client_id = "A"
        gui._evaluate_expr("x + y = {x + y}")
        g.client_id = "B"
        gui._evaluate_expr("x")
        gui._re_evaluate_expr("x")
