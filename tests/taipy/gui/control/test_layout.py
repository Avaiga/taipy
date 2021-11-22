from taipy.gui import Gui


def test_layout_md_1(gui: Gui, helpers):
    md_string = """
<|layout|type=1 1|gap=1rem|
# This is a layout section
|>
"""
    expected_list = ["<Layout", 'type="1 1', 'gap="1rem"', "<h1", "This is a layout section"]
    helpers.test_control_md(gui, md_string, expected_list)


def test_layout_md_2(gui: Gui, helpers):
    md_string = """
<|layout.start|type=1 1|gap=1rem|>
# This is a layout section
<|layout.end|>
"""
    expected_list = ["<Layout", 'type="1 1', 'gap="1rem"', "<h1", "This is a layout section"]
    helpers.test_control_md(gui, md_string, expected_list)


def test_layout_html(gui: Gui, helpers):
    html_string = '<taipy:layout type="1 1" gap="1rem"><h1>This is a layout section</h1></taipy:layout>'
    expected_list = ["<Layout", 'type="1 1', 'gap="1rem"', "<h1", "This is a layout section"]
    helpers.test_control_html(gui, html_string, expected_list)
