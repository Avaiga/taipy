from taipy.gui import Gui


def test_number_md_1(gui: Gui, helpers):
    md_string = "<|10|number|>"
    expected_list = ["<Input", 'value="10"', 'type="number"']
    helpers.test_control_md(gui, md_string, expected_list, check_warning=False)


def test_number_md_2(gui: Gui, helpers):
    gui.bind_var_val("x", "10")
    md_string = "<|{x}|number|>"
    expected_list = ["<Input", 'tp_varname="x"', 'defaultValue="10"', 'type="number"', "value={x}"]
    helpers.test_control_md(gui, md_string, expected_list)


def test_number_html_1(gui: Gui, helpers):
    gui.bind_var_val("x", 10)
    html_string = '<taipy:number value="{x}" />'
    expected_list = ["<Input", 'tp_varname="x"', 'defaultValue="10"', 'type="number"', "value={x}"]
    helpers.test_control_html(gui, html_string, expected_list)


def test_number_html_2(gui: Gui, helpers):
    gui.bind_var_val("x", 10)
    html_string = "<taipy:number>{x}</taipy:number>"
    expected_list = ["<Input", 'tp_varname="x"', 'defaultValue="10"', 'type="number"', "value={x}"]
    helpers.test_control_html(gui, html_string, expected_list)
