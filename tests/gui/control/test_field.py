from taipy.gui import Gui


def test_field_md_1(gui: Gui, helpers):
    gui.bind_var_val("x", 10)
    md_string = "<|{x}|>"
    expected_list = ["<Field", 'dataType="int"', 'defaultValue="10"', "value={x}"]
    helpers.test_control_md(gui, md_string, expected_list)


def test_field_html_1(gui: Gui, helpers):
    gui.bind_var_val("x", 10)
    html_string = '<taipy:field value="{x}" />'
    expected_list = ["<Field", 'dataType="int"', 'defaultValue="10"', "value={x}"]
    helpers.test_control_html(gui, html_string, expected_list)


def test_field_html_2(gui: Gui, helpers):
    gui.bind_var_val("x", 10)
    html_string = "<taipy:field>{x}</taipy:field>"
    expected_list = ["<Field", 'dataType="int"', 'defaultValue="10"', "value={x}"]
    helpers.test_control_html(gui, html_string, expected_list)
