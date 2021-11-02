from taipy.gui import Gui


def test_field_1(gui: Gui, helpers):
    gui.bind_var_val("x", 10)
    md_string = "x = <|{x}|>"
    expected_list = ["x = <Field", 'dataType="int"', 'defaultValue="10"', "value={x}"]
    helpers.test_control(gui, md_string, expected_list)


def test_field_2(gui: Gui, helpers):
    gui.bind_var_val("x", 10)
    md_string = "x = <|{x}|>"
    expected_str = '<div class="md-para" key="div.0">x = <Field className="taipy-field " dataType="int" defaultValue="10" key="Field.0" value={x}></Field></div>'
    helpers.test_control(gui, md_string, expected_str)
