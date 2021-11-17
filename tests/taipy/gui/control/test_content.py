from taipy.gui import Gui


def test_content_md(gui: Gui, helpers):
    md_string = "<|content|>"
    expected_list = ["<PageContent"]
    helpers.test_control_md(gui, md_string, expected_list)


def test_content_html(gui: Gui, helpers):
    html_string = "<taipy:content />"
    expected_list = ["<PageContent"]
    helpers.test_control_html(gui, html_string, expected_list)
