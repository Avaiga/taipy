from types import FunctionType
import pandas as pd  # type: ignore

from taipy.gui import Gui


def test_expression_field_control_str(gui: Gui, helpers):
    gui.bind_var_val("x", "Hello World!")
    md_string = "<|{x}|>"
    expected_list = ["<Field", 'dataType="str"', 'defaultValue="Hello World!"', "value={x}"]
    helpers.test_control_md(gui, md_string, expected_list)


def test_expression_field_control_int(gui: Gui, helpers):
    gui.bind_var_val("x", 10)
    md_string = "<|{x}|>"
    expected_list = ["<Field", 'dataType="int"', 'defaultValue="10"', "value={x}"]
    helpers.test_control_md(gui, md_string, expected_list)


def test_expression_field_control_1(gui: Gui, helpers):
    gui.bind_var_val("x", 10)
    gui.bind_var_val("y", 20)
    md_string = "<|{x + y}|>"
    expected_list = ["<Field", 'dataType="int"', 'defaultValue="30"', "value={tp_x_y_0}"]
    helpers.test_control_md(gui, md_string, expected_list)


def test_expression_field_control_2(gui: Gui, helpers):
    gui.bind_var_val("x", 10)
    gui.bind_var_val("y", 20)
    md_string = "<|x + y = {x + y}|>"
    expected_list = ["<Field", 'dataType="str"', 'defaultValue="x + y = 30"', "value={tp_x_y_x_y__0}"]
    helpers.test_control_md(gui, md_string, expected_list)


def test_expression_field_control_3(gui: Gui, helpers):
    gui.bind_var_val("x", "Mickey Mouse")
    gui.bind_var_val("y", "Donald Duck")
    md_string = "<|Hello {x} and {y}|>"
    expected_list = [
        "<Field",
        'dataType="str"',
        'defaultValue="Hello Mickey Mouse and Donald Duck"',
        "value={tp_Hello_x_and_y__0}",
    ]
    helpers.test_control_md(gui, md_string, expected_list)


def test_expression_field_gt_operator(gui: Gui, helpers):
    gui.bind_var_val("x", 0)
    md_string = "<|{x > 0}|>"
    expected_list = ["<Field", 'dataType="bool"', 'defaultValue="false"', "value={tp_x_0_0}"]
    helpers.test_control_md(gui, md_string, expected_list)


def test_expression_button_control(gui: Gui, helpers):
    gui.bind_var_val("label", "A button label")
    md_string = "<|button|label={label}|>"
    expected_list = ["<Button", 'defaultValue="A button label"', "value={label}"]
    helpers.test_control_md(gui, md_string, expected_list)


def test_expression_table_control(gui: Gui, helpers):
    gui.bind_var_val("pd", pd)
    gui.bind_var_val("series_1", pd.Series(["a", "b", "c"], name="Letters"))
    gui.bind_var_val("series_2", pd.Series([1, 2, 3], name="Numbers"))
    md_string = "<|{pd.concat([series_1, series_2], axis=1)}|table|page_size=10|columns=Letters;Numbers|>"
    expected_list = [
        "<Table",
        'columns="{&quot;Letters&quot;: {&quot;index&quot;: 0, &quot;type&quot;: &quot;object&quot;, &quot;dfid&quot;: &quot;Letters&quot;}, &quot;Numbers&quot;: {&quot;index&quot;: 1, &quot;type&quot;: &quot;int64&quot;, &quot;dfid&quot;: &quot;Numbers&quot;}}"',
        "refresh={tp_pd_concat_series_1_series_2_axis_1__0__refresh}",
        'tp_varname="pd.concat([series_1, series_2], axis=1)"',
        "value={tp_pd_concat_series_1_series_2_axis_1__0}",
    ]
    helpers.test_control_md(gui, md_string, expected_list)
    assert isinstance(gui._get_data_scope().tp_pd_concat_series_1_series_2_axis_1__0, pd.DataFrame)


def test_lambda_expression_selector(gui: Gui, helpers):
    gui.bind_var_val(
        "lov",
        [
            {"id": "1", "name": "scenario 1"},
            {"id": "3", "name": "scenario 3"},
            {"id": "2", "name": "scenario 2"},
        ],
    )
    gui.bind_var_val("sel", {"id": "1", "name": "scenario 1"})
    md_string = "<|{sel}|selector|lov={lov}|type=test|adapter={lambda elt: (elt['id'], elt['name'])}|>"
    expected_list = [
        "<Selector",
        'defaultLov="[[&quot;1&quot;, &quot;scenario 1&quot;], [&quot;3&quot;, &quot;scenario 3&quot;], [&quot;2&quot;, &quot;scenario 2&quot;]]"',
        'defaultValue="[&quot;1&quot;]"',
        'tp_updatevars="lov=lov"',
        'tp_varname="sel"',
        "value={sel}",
    ]
    helpers.test_control_md(gui, md_string, expected_list)
