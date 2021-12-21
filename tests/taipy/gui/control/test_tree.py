from taipy.gui import Gui


def test_tree_md(gui: Gui, helpers):
    gui.bind_var_val("value", "Item 1")
    md_string = "<|{value}|tree|lov=Item 1;Item 2;Item 3|>"
    expected_list = [
        "<TreeView",
        'defaultLov="[[&quot;Item 1&quot;, &quot;Item 1&quot;], [&quot;Item 2&quot;, &quot;Item 2&quot;], [&quot;Item 3&quot;, &quot;Item 3&quot;]]"',
        'defaultValue="[&quot;Item 1&quot;]"',
        'tp_varname="value"',
        "value={value}",
    ]
    helpers.test_control_md(gui, md_string, expected_list)


def test_tree_html_1(gui: Gui, helpers):
    gui.bind_var_val("value", "Item 1")
    html_string = '<taipy:tree lov="Item 1;Item 2;Item 3">{value}</taipy:tree>'
    expected_list = [
        "<TreeView",
        'defaultLov="[[&quot;Item 1&quot;, &quot;Item 1&quot;], [&quot;Item 2&quot;, &quot;Item 2&quot;], [&quot;Item 3&quot;, &quot;Item 3&quot;]]"',
        'defaultValue="[&quot;Item 1&quot;]"',
        'tp_varname="value"',
        "value={value}",
    ]
    helpers.test_control_html(gui, html_string, expected_list)


def test_tree_html_2(gui: Gui, helpers):
    gui.bind_var_val("value", "Item 1")
    html_string = '<taipy:tree lov="Item 1;Item 2;Item 3" value="{value}" />'
    expected_list = [
        "<TreeView",
        'defaultLov="[[&quot;Item 1&quot;, &quot;Item 1&quot;], [&quot;Item 2&quot;, &quot;Item 2&quot;], [&quot;Item 3&quot;, &quot;Item 3&quot;]]"',
        'defaultValue="[&quot;Item 1&quot;]"',
        'tp_varname="value"',
        "value={value}",
    ]
    helpers.test_control_html(gui, html_string, expected_list)
