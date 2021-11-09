from taipy.gui import Gui


def test_input_md(gui: Gui, helpers):
    gui.bind_var_val("x", "Hello World!")
    md_string = "<|{x}|input|>"
    expected_list = ["<Input", 'tp_varname="x"', 'defaultValue="Hello World!"', 'type="text"', "value={x}"]
    helpers.test_control_md(gui, md_string, expected_list)


def test_input_html_1(gui: Gui, helpers):
    gui.bind_var_val("x", "Hello World!")
    html_string = '<taipy:input value="{x}" />'
    expected_list = ["<Input", 'tp_varname="x"', 'defaultValue="Hello World!"', 'type="text"', "value={x}"]
    helpers.test_control_html(gui, html_string, expected_list)


def test_input_html_2(gui: Gui, helpers):
    gui.bind_var_val("x", "Hello World!")
    html_string = "<taipy:input>{x}</taipy:input>"
    expected_list = ["<Input", 'tp_varname="x"', 'defaultValue="Hello World!"', 'type="text"', "value={x}"]
    helpers.test_control_html(gui, html_string, expected_list)
