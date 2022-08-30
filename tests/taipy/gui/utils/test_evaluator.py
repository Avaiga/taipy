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

import inspect
import warnings

from taipy.gui import Gui
from taipy.gui.utils.types import _TaipyNumber


def test_unbind_variable_in_expression(gui: Gui):
    gui.run(run_server=False, single_client=True)
    with warnings.catch_warnings(record=True) as records:
        with gui.get_flask_app().app_context():
            gui._evaluate_expr("{x}")
            assert len(records) == 3
            assert "Variable 'x' is not available in" in str(records[0].message)
            assert "Variable 'x' is not defined" in str(records[1].message)
            assert "Cannot evaluate expression 'x': name 'x' is not defined" in str(records[2].message)


def test_evaluate_same_expression_multiple_times(gui: Gui):
    x = 10  # noqa: F841
    gui._set_frame(inspect.currentframe())
    gui.run(run_server=False, single_client=True)
    with gui.get_flask_app().app_context():
        s1 = gui._evaluate_expr("x + 10 = {x + 10}")
        s2 = gui._evaluate_expr("x + 10 = {x + 10}")
        assert s1 == s2


def test_evaluate_expressions_same_variable(gui: Gui):
    x = 10  # noqa: F841
    gui._set_frame(inspect.currentframe())
    gui.run(run_server=False, single_client=True)
    with gui.get_flask_app().app_context():
        s1 = gui._evaluate_expr("x + 10 = {x + 10}")
        s2 = gui._evaluate_expr("x = {x}")
        assert "tp_TpExPr_x" in s1 and "tp_TpExPr_x" in s2


def test_evaluate_holder(gui: Gui, test_client):
    x = 10  # noqa: F841
    gui._set_frame(inspect.currentframe())
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
    gui.run(run_server=False)
    with gui.get_flask_app().app_context():
        assert "x + 10" == gui._evaluate_expr("x + 10")
