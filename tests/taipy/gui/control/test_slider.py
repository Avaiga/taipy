from taipy.gui import Gui


def test_slider_md(gui: Gui, helpers):
    gui._bind_var_val("x", 10)
    md_string = "<|{x}|slider|>"
    expected_list = ["<Slider", 'updateVarName="_TpN_x', "defaultValue={10}", "value={_TpN_x}"]
    helpers.test_control_md(gui, md_string, expected_list)


def test_slider_with_min_max(gui: Gui, helpers):
    gui._bind_var_val("x", 0)
    md_string = "<|{x}|slider|min=-10|max=10|>"
    expected_list = ["<Slider", "min={-10.0}", "max={10.0}", "defaultValue={0}"]
    helpers.test_control_md(gui, md_string, expected_list)


def test_slider_items_md(gui: Gui, helpers):
    gui._bind_var_val("x", "Item 1")
    md_string = "<|{x}|slider|lov=Item 1;Item 2;Item 3|text_anchor=left|>"
    expected_list = [
        "<Slider",
        'updateVarName="_TpLv_x"',
        "value={_TpLv_x}",
        'defaultLov="[&quot;Item 1&quot;, &quot;Item 2&quot;, &quot;Item 3&quot;]"',
        'defaultValue="[&quot;Item 1&quot;]"',
        'textAnchor="left"',
    ]
    helpers.test_control_md(gui, md_string, expected_list)


def test_slider_text_anchor_md(gui: Gui, helpers):
    gui._bind_var_val("x", "Item 1")
    md_string = "<|{x}|slider|text_anchor=NoNe|>"
    expected_list = ["<Slider", 'updateVarName="_TpN_x"', "value={_TpN_x}", 'textAnchor="none"']
    helpers.test_control_md(gui, md_string, expected_list)


def test_slider_text_anchor_default_md(gui: Gui, helpers):
    gui._bind_var_val("x", "Item 1")
    md_string = "<|{x}|slider|items=Item 1|>"
    expected_list = ["<Slider", 'updateVarName="_TpN_x"', "value={_TpN_x}", 'textAnchor="bottom"']
    helpers.test_control_md(gui, md_string, expected_list)


def test_slider_html_1(gui: Gui, helpers):
    gui._bind_var_val("x", 10)
    html_string = '<taipy:slider value="{x}" />'
    expected_list = ["<Slider", 'updateVarName="_TpN_x"', "defaultValue={10}", "value={_TpN_x}"]
    helpers.test_control_html(gui, html_string, expected_list)


def test_slider_html_2(gui: Gui, helpers):
    gui._bind_var_val("x", 10)
    html_string = "<taipy:slider>{x}</taipy:slider>"
    expected_list = ["<Slider", 'updateVarName="_TpN_x"', "defaultValue={10}", "value={_TpN_x}"]
    helpers.test_control_html(gui, html_string, expected_list)
