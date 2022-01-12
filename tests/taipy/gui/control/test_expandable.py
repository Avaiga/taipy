from taipy.gui import Gui


def test_expandable_md_1(gui: Gui, helpers):
    md_string = """
<|Expandable section|expandable|not expanded|
# This is an expandable section
|>
"""
    expected_list = [
        "<Expandable",
        "expanded={false}",
        'title="Expandable section"',
        "<h1",
        "This is an expandable section",
    ]
    helpers.test_control_md(gui, md_string, expected_list, check_warning=False)


def test_expandable_md_2(gui: Gui, helpers):
    md_string = """
<|expandable.start|title=Expandable section|not expanded|>
# This is an expandable section
<|expandable.end|>
"""
    expected_list = [
        "<Expandable",
        "expanded={false}",
        'title="Expandable section"',
        "<h1",
        "This is an expandable section",
    ]
    helpers.test_control_md(gui, md_string, expected_list, check_warning=False)


def test_expandable_html(gui: Gui, helpers):
    html_string = '<taipy:expandable title="Expandable section" expanded="false"><h1>This is an expandable section</h1></taipy:expandable >'
    expected_list = [
        "<Expandable",
        "expanded={false}",
        'title="Expandable section"',
        "<h1",
        "This is an expandable section",
    ]
    helpers.test_control_html(gui, html_string, expected_list, check_warning=False)
