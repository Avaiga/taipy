from taipy.gui import Gui


def test_slider_md(gui: Gui, helpers):
    gui.bind_var_val("x", 10)
    md_string = "<|{x}|slider|>"
    expected_list = ["<Slider", 'tp_varname="x"', 'defaultValue="10"', "value={x}"]
    helpers.test_control_md(gui, md_string, expected_list)


def test_slider_html_1(gui: Gui, helpers):
    gui.bind_var_val("x", 10)
    html_string = '<taipy:slider value="{x}" />'
    expected_list = ["<Slider", 'tp_varname="x"', 'defaultValue="10"', "value={x}"]
    helpers.test_control_html(gui, html_string, expected_list)


def test_slider_html_2(gui: Gui, helpers):
    gui.bind_var_val("x", 10)
    html_string = "<taipy:slider>{x}</taipy:slider>"
    expected_list = ["<Slider", 'tp_varname="x"', 'defaultValue="10"', "value={x}"]
    helpers.test_control_html(gui, html_string, expected_list)
