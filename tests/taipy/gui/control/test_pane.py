from taipy.gui import Gui


def test_pane_md(gui: Gui, helpers):
    gui.bind_var_val("show_pane", False)
    md_string = """
<|{show_pane}|pane|not persistent|
# This is a Pane
|>
"""
    expected_list = [
        "<Pane",
        'anchor="left"',
        "defaultOpen={false}",
        "persistent={false}",
        'tp_varname="show_pane"',
        "open={show_pane}",
        "<h1",
        "This is a Pane</h1></Pane>",
    ]
    helpers.test_control_md(gui, md_string, expected_list)


def test_pane_html(gui: Gui, helpers):
    gui.bind_var_val("show_pane", False)
    html_string = '<taipy:pane open="{show_pane}" persistent="false"><h1>This is a Pane</h1></taipy:pane>'
    expected_list = [
        "<Pane",
        'anchor="left"',
        "defaultOpen={false}",
        "persistent={false}",
        'tp_varname="show_pane"',
        "open={show_pane}",
        "<h1",
        "This is a Pane</h1></Pane>",
    ]
    helpers.test_control_html(gui, html_string, expected_list)
