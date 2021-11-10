from taipy.gui import Gui


def test_selector_md_1(gui: Gui, helpers):
    gui.bind_var_val("selected_val", ["l1", "l2"])
    gui.bind_var_val("selector_properties", {"lov": [("l1", "v1"), ("l2", "v2"), ("l3", "v3")], "filter": True})
    md_string = "<|{selected_val}|selector|properties=selector_properties|multiple|>"
    expected_list = [
        "<Selector",
        'defaultLov="[[&quot;l1&quot;, &quot;v1&quot;], [&quot;l2&quot;, &quot;v2&quot;], [&quot;l3&quot;, &quot;v3&quot;]]"',
        'defaultValue="[&quot;-1&quot;, &quot;-1&quot;]"',
        "filter={true}",
        "multiple={true}",
        'tp_varname="selected_val"',
        "value={selected_val}",
    ]
    helpers.test_control_md(gui, md_string, expected_list)


def test_selector_md_2(gui: Gui, helpers):
    gui.bind_var_val("selected_val", "Item 2")
    md_string = "<|{selected_val}|selector|lov=Item 1;Item 2; This is a another value|>"
    expected_list = [
        "<Selector",
        'defaultLov="[[&quot;Item 1&quot;, &quot;Item 1&quot;], [&quot;Item 2&quot;, &quot;Item 2&quot;], [&quot; This is a another value&quot;, &quot; This is a another value&quot;]]"',
        'defaultValue="[&quot;Item 2&quot;]"',
        'tp_varname="selected_val"',
        "value={selected_val}",
    ]
    helpers.test_control_md(gui, md_string, expected_list)


def test_selector_md_3(gui: Gui, helpers):
    gui.bind_var_val("elt", None)
    gui.bind_var_val(
        "scenario_list",
        [{"id": "1", "name": "scenario 1"}, {"id": "3", "name": "scenario 3"}, {"id": "2", "name": "scenario 2"}],
    )
    gui.bind_var_val("selected_obj", {"id": "1", "name": "scenario 1"})
    md_string = '<|{selected_obj}|selector|lov={scenario_list}|type=Scenario|adapter={lambda elt: (elt["id"], elt["name"])}|not propagate|>'
    expected_list = [
        "<Selector",
        'defaultLov="[[&quot;1&quot;, &quot;scenario 1&quot;], [&quot;3&quot;, &quot;scenario 3&quot;], [&quot;2&quot;, &quot;scenario 2&quot;]]"',
        'defaultValue="[&quot;1&quot;]"',
        "lov={scenario_list}",
        "propagate={false}",
        'tp_updatevars="lov=scenario_list"',
        'tp_varname="selected_obj"',
        "value={selected_obj}",
    ]
    helpers.test_control_md(gui, md_string, expected_list)


def test_selector_html_1_1(gui: Gui, helpers):
    gui.bind_var_val("selected_val", ["l1", "l2"])
    gui.bind_var_val("selector_properties", {"lov": [("l1", "v1"), ("l2", "v2"), ("l3", "v3")], "filter": True})
    html_string = '<taipy:selector value="{selected_val}" properties="selector_properties" multiple="True"/>'
    expected_list = [
        "<Selector",
        'defaultLov="[[&quot;l1&quot;, &quot;v1&quot;], [&quot;l2&quot;, &quot;v2&quot;], [&quot;l3&quot;, &quot;v3&quot;]]"',
        'defaultValue="[&quot;-1&quot;, &quot;-1&quot;]"',
        "filter={true}",
        "multiple={true}",
        'tp_varname="selected_val"',
        "value={selected_val}",
    ]
    helpers.test_control_html(gui, html_string, expected_list)


def test_selector_html_1_2(gui: Gui, helpers):
    gui.bind_var_val("selected_val", ["l1", "l2"])
    gui.bind_var_val("selector_properties", {"lov": [("l1", "v1"), ("l2", "v2"), ("l3", "v3")], "filter": True})
    html_string = '<taipy:selector properties="selector_properties" multiple="True">{selected_val}</taipy:selector>'
    expected_list = [
        "<Selector",
        'defaultLov="[[&quot;l1&quot;, &quot;v1&quot;], [&quot;l2&quot;, &quot;v2&quot;], [&quot;l3&quot;, &quot;v3&quot;]]"',
        'defaultValue="[&quot;-1&quot;, &quot;-1&quot;]"',
        "filter={true}",
        "multiple={true}",
        'tp_varname="selected_val"',
        "value={selected_val}",
    ]
    helpers.test_control_html(gui, html_string, expected_list)


def test_selector_html_2_1(gui: Gui, helpers):
    gui.bind_var_val("selected_val", "Item 2")
    html_string = '<taipy:selector value="{selected_val}" lov="Item 1;Item 2; This is a another value" />'
    expected_list = [
        "<Selector",
        'defaultLov="[[&quot;Item 1&quot;, &quot;Item 1&quot;], [&quot;Item 2&quot;, &quot;Item 2&quot;], [&quot; This is a another value&quot;, &quot; This is a another value&quot;]]"',
        'defaultValue="[&quot;Item 2&quot;]"',
        'tp_varname="selected_val"',
        "value={selected_val}",
    ]
    helpers.test_control_html(gui, html_string, expected_list)


def test_selector_html_2_2(gui: Gui, helpers):
    gui.bind_var_val("selected_val", "Item 2")
    html_string = '<taipy:selector lov="Item 1;Item 2; This is a another value">{selected_val}</taipy:selector>'
    expected_list = [
        "<Selector",
        'defaultLov="[[&quot;Item 1&quot;, &quot;Item 1&quot;], [&quot;Item 2&quot;, &quot;Item 2&quot;], [&quot; This is a another value&quot;, &quot; This is a another value&quot;]]"',
        'defaultValue="[&quot;Item 2&quot;]"',
        'tp_varname="selected_val"',
        "value={selected_val}",
    ]
    helpers.test_control_html(gui, html_string, expected_list)
