from taipy.gui import Gui


def test_toggle_md_1(gui: Gui, helpers):
    md_string = "<|toggle|theme|>"
    expected_list = ["<Toggle", 'kind="theme"', 'unselectedValue=""']
    helpers.test_control_md(gui, md_string, expected_list, check_warning=False)


def test_toggle_md_2(gui: Gui, helpers):
    gui.bind_var_val("x", "l1")
    gui.bind_var_val("lov", [("l1", "v1"), ("l2", "v2")])
    md_string = "<|{x}|toggle|lov={lov}|label=Label|>"
    expected_list = [
        "<Toggle",
        'defaultLov="[[&quot;l1&quot;, &quot;v1&quot;], [&quot;l2&quot;, &quot;v2&quot;]]"',
        'defaultValue="l1"',
        'label="Label"',
        "lov={TaipyLov_lov}",
        'tp_updatevars="lov=TaipyLov_lov"',
        'tp_varname="TaipyLovValue_x"',
        'unselectedValue=""',
        "value={TaipyLovValue_x}",
    ]
    helpers.test_control_md(gui, md_string, expected_list)


def test_toggle_html_1(gui: Gui, helpers):
    html_string = '<taipy:toggle theme="True" />'
    expected_list = ["<Toggle", 'kind="theme"', 'unselectedValue=""']
    helpers.test_control_html(gui, html_string, expected_list, check_warning=False)


def test_toggle_html_2(gui: Gui, helpers):
    gui.bind_var_val("x", "l1")
    gui.bind_var_val("lov", [("l1", "v1"), ("l2", "v2")])
    html_string = '<taipy:toggle lov="{lov}" label="Label">{x}</taipy:toggle>'
    expected_list = [
        "<Toggle",
        'defaultLov="[[&quot;l1&quot;, &quot;v1&quot;], [&quot;l2&quot;, &quot;v2&quot;]]"',
        'defaultValue="l1"',
        'label="Label"',
        "lov={TaipyLov_lov}",
        'tp_updatevars="lov=TaipyLov_lov"',
        'tp_varname="TaipyLovValue_x"',
        'unselectedValue=""',
        "value={TaipyLovValue_x}",
    ]
    helpers.test_control_html(gui, html_string, expected_list)
