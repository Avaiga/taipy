import os
from importlib import util
from pathlib import Path

if util.find_spec("playwright"):
    from playwright._impl._page import Page

from taipy.gui import Gui, Html


def test_html_render_with_style(page: "Page", gui: Gui, helpers):
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <style>
        .taipy-text {
            color: green;
        }
        .custom-text {
            color: blue;
        }
    </style>
</head>
<body>
    <taipy:text id="text1">Hey</taipy:text>
    <taipy:text id="text2" class="custom-text">There</taipy:text>
</body>
</html>"""
    gui.add_page("page1", Html(html_content))
    helpers.run_e2e(gui)
    page.goto("/page1")
    page.expect_websocket()
    page.wait_for_selector("#text1")
    assert (
        page.evaluate('window.getComputedStyle(document.querySelector("#text1"), null).getPropertyValue("color")')
        == "rgb(0, 128, 0)"
    )
    assert (
        page.evaluate('window.getComputedStyle(document.querySelector("#text2"), null).getPropertyValue("color")')
        == "rgb(0, 0, 255)"
    )


def test_html_render_bind_assets(page: "Page", gui: Gui, helpers):
    gui.add_pages(pages=f"{Path(Path(__file__).parent.resolve())}{os.path.sep}page_assets")
    helpers.run_e2e(gui)
    page.goto("/page1")
    page.expect_websocket()
    page.wait_for_selector("#text1")
    assert (
        page.evaluate('window.getComputedStyle(document.querySelector("#text1"), null).getPropertyValue("color")')
        == "rgb(0, 128, 0)"
    )
    assert (
        page.evaluate('window.getComputedStyle(document.querySelector("#text2"), null).getPropertyValue("color")')
        == "rgb(0, 0, 255)"
    )
