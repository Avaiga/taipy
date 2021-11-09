from taipy.gui import Gui


def test_toggle_md_1(gui: Gui, helpers):
    md_string = "<|toggle|theme|>"
    expected_list = ["<Toggle", 'kind="theme"', 'unselectedValue=""', 'value=""']
    helpers.test_control_md(gui, md_string, expected_list)


def test_toggle_md_2(gui: Gui, helpers):
    gui.bind_var_val("x", "l1")
    gui.bind_var_val("lov", [("l1", "v1"), ("l2", "v2")])
    md_string = "<|{x}|toggle|lov={lov}|label=Label|>"
    expected_list = [
        "<Toggle",
        'defaultLov="[[&quot;l1&quot;, &quot;v1&quot;], [&quot;l2&quot;, &quot;v2&quot;]]"',
        'defaultValue="-1"',
        'label="Label"',
        "lov={lov}",
        'tp_updatevars="lov=lov"',
        'tp_varname="x"',
        'unselectedValue=""',
        "value={x}",
    ]
    helpers.test_control_md(gui, md_string, expected_list)


def test_toggle_html_1(gui: Gui, helpers):
    html_string = '<taipy:toggle theme="True" />'
    expected_list = ["<Toggle", 'kind="theme"', 'unselectedValue=""', 'value=""']
    helpers.test_control_html(gui, html_string, expected_list)


def test_toggle_html_2(gui: Gui, helpers):
    gui.bind_var_val("x", "l1")
    gui.bind_var_val("lov", [("l1", "v1"), ("l2", "v2")])
    html_string = '<taipy:toggle lov="{lov}" label="Label">{x}</taipy:toggle>'
    expected_list = [
        "<Toggle",
        'defaultLov="[[&quot;l1&quot;, &quot;v1&quot;], [&quot;l2&quot;, &quot;v2&quot;]]"',
        'defaultValue="-1"',
        'label="Label"',
        "lov={lov}",
        'tp_updatevars="lov=lov"',
        'tp_varname="x"',
        'unselectedValue=""',
        "value={x}",
    ]
    helpers.test_control_html(gui, html_string, expected_list)
