from taipy.gui import Gui


def test_part_md_1(gui: Gui, helpers):
    md_string = """
<|part|class_name=class1|
# This is a part
|>
"""
    expected_list = ["<Part", "<h1", "This is a part"]
    helpers.test_control_md(gui, md_string, expected_list)


def test_part_md_2(gui: Gui, helpers):
    md_string = """
<|part.start|class_name=class1|>
# This is a part
<|part.end|>
"""
    expected_list = ["<Part", "<h1", "This is a part"]
    helpers.test_control_md(gui, md_string, expected_list)


def test_part_html(gui: Gui, helpers):
    html_string = '<taipy:part class_name="class1"><h1>This is a part</h1></taipy:part>'
    expected_list = ["<Part", "<h1", "This is a part"]
    helpers.test_control_html(gui, html_string, expected_list)
