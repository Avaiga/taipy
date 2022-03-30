import inspect
import os
import time
from importlib import util
from pathlib import Path
from urllib.request import urlopen

if util.find_spec("playwright"):
    from playwright._impl._page import Page

from taipy.gui import Gui, Html
from taipy.gui.server import _Server


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
    gui._set_frame(inspect.currentframe())
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
    gui._set_frame(inspect.currentframe())
    gui.add_pages(pages=f"{Path(Path(__file__).parent.resolve())}{os.path.sep}test-assets")
    helpers.run_e2e(gui)
    assert ".taipy-text" in urlopen("http://127.0.0.1:5000/test-assets/style/style.css").read().decode("utf-8")
    page.goto("/test-assets/page1")
    page.expect_websocket()
    page.wait_for_selector("#text1")
    retry = 0
    while (
        retry < 10
        and page.evaluate('window.getComputedStyle(document.querySelector("#text1"), null).getPropertyValue("color")')
        != "rgb(0, 128, 0)"
    ):
        retry += 1
        time.sleep(0.1)
    assert (
        page.evaluate('window.getComputedStyle(document.querySelector("#text1"), null).getPropertyValue("color")')
        == "rgb(0, 128, 0)"
    )
    assert (
        page.evaluate('window.getComputedStyle(document.querySelector("#text2"), null).getPropertyValue("color")')
        == "rgb(0, 0, 255)"
    )


def test_html_render_path_mapping(page: "Page", gui: Gui, helpers):
    gui._server = _Server(
        gui,
        path_mapping={"style": f"{Path(Path(__file__).parent.resolve())}{os.path.sep}test-assets{os.path.sep}style"},
    )
    gui.add_page("page1", Html(f"{Path(Path(__file__).parent.resolve())}{os.path.sep}page1.html"))
    helpers.run_e2e(gui)
    assert ".taipy-text" in urlopen("http://127.0.0.1:5000/style/style.css").read().decode("utf-8")
    page.goto("/page1")
    page.expect_websocket()
    page.wait_for_selector("#text1")
    retry = 0
    while (
        retry < 10
        and page.evaluate('window.getComputedStyle(document.querySelector("#text1"), null).getPropertyValue("color")')
        != "rgb(0, 128, 0)"
    ):
        retry += 1
        time.sleep(0.1)
    assert (
        page.evaluate('window.getComputedStyle(document.querySelector("#text1"), null).getPropertyValue("color")')
        == "rgb(0, 128, 0)"
    )
    assert (
        page.evaluate('window.getComputedStyle(document.querySelector("#text2"), null).getPropertyValue("color")')
        == "rgb(0, 0, 255)"
    )
