import inspect
import warnings

from taipy.gui import Gui
from taipy.gui.utils.types import _TaipyNumber


def test_unbind_variable_in_expression(gui: Gui):
    gui.run(run_server=False)
    with warnings.catch_warnings(record=True) as records:
        gui._evaluate_expr("{x}")
        assert len(records) == 2
        assert "Variable 'x' is not defined" in str(records[0].message)
        assert "Cannot evaluate expression 'x': name 'x' is not defined" in str(records[1].message)


def test_evaluate_same_expression_multiple_times(gui: Gui):
    x = 10
    gui._set_frame(inspect.currentframe())
    gui.run(run_server=False)
    s1 = gui._evaluate_expr("x + 10 = {x + 10}")
    s2 = gui._evaluate_expr("x + 10 = {x + 10}")
    assert s1 == s2


def test_evaluate_expressions_same_variable(gui: Gui):
    x = 10
    gui._set_frame(inspect.currentframe())
    gui.run(run_server=False)
    s1 = gui._evaluate_expr("x + 10 = {x + 10}")
    s2 = gui._evaluate_expr("x = {x}")
    assert "tp_x" in s1 and "tp_x" in s2


def test_evaluate_holder(gui: Gui):
    x = 10
    gui._set_frame(inspect.currentframe())
    gui.run(run_server=False)
    with warnings.catch_warnings(record=True) as w:
        gui._evaluate_expr("{x + 10}")
        hash = gui._evaluate_bind_holder(_TaipyNumber, "x + 10")
        assert "_TpN_tp_x_10_" in hash
        lst = gui._evaluate_holders("x + 10")
        assert len(lst) == 1
        assert "_TpN_tp_x_10_" in lst[0]
        # test re-evaluate holders
        gui._bindings().x = 20
        gui._re_evaluate_expr(lst[0])


def test_evaluate_not_expression_type(gui: Gui):
    gui.run(run_server=False)
    assert "x + 10" == gui._evaluate_expr("x + 10")
