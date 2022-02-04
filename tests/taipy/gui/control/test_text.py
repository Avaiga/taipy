from taipy.gui import Gui


def test_text_md_1(gui: Gui, helpers):
    gui.bind_var_val("x", 10)
    md_string = "<|{x}|>"
    expected_list = ["<Field", 'dataType="int"', 'defaultValue="10"', "value={x}"]
    helpers.test_control_md(gui, md_string, expected_list)


def test_text_html_1(gui: Gui, helpers):
    gui.bind_var_val("x", 10)
    html_string = '<taipy:text value="{x}" />'
    expected_list = ["<Field", 'dataType="int"', 'defaultValue="10"', "value={x}"]
    helpers.test_control_html(gui, html_string, expected_list)


def test_text_html_2(gui: Gui, helpers):
    gui.bind_var_val("x", 10)
    html_string = "<taipy:text>{x}</taipy:text>"
    expected_list = ["<Field", 'dataType="int"', 'defaultValue="10"', "value={x}"]
    helpers.test_control_html(gui, html_string, expected_list)
