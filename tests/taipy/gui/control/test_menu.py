from taipy.gui import Gui


def test_menu_md(gui: Gui, helpers):
    gui._bind_var_val("lov", ["Item 1", "Item 2", "Item 3", "Item 4"])
    md_string = "<|menu|lov={lov}|>"
    expected_list = [
        "<MenuCtl",
        'className="taipy-menu"',
        'defaultLov="[&quot;Item 1&quot;, &quot;Item 2&quot;, &quot;Item 3&quot;, &quot;Item 4&quot;]"',
        "lov={_TpL_lov}",
        'tp_onAction="on_menu_action"',
        'updateVars="lov=_TpL_lov"',
    ]
    helpers.test_control_md(gui, md_string, expected_list)


def test_menu_html(gui: Gui, helpers):
    gui._bind_var_val("lov", ["Item 1", "Item 2", "Item 3", "Item 4"])
    html_string = '<taipy:menu lov="{lov}" />'
    expected_list = [
        "<MenuCtl",
        'className="taipy-menu"',
        'defaultLov="[&quot;Item 1&quot;, &quot;Item 2&quot;, &quot;Item 3&quot;, &quot;Item 4&quot;]"',
        "lov={_TpL_lov}",
        'tp_onAction="on_menu_action"',
        'updateVars="lov=_TpL_lov"',
    ]
    helpers.test_control_html(gui, html_string, expected_list)
