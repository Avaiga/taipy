from importlib import util
import inspect

import pytest

if util.find_spec("playwright"):
    from playwright._impl._page import Page

from taipy.gui import Gui


@pytest.mark.teste2e
def test_theme_light(page: "Page", gui: Gui, helpers):
    page_md = """
<|Just a page|id=text1|>
"""
    gui._set_frame(inspect.currentframe())
    gui.add_page(name="test", page=page_md)
    helpers.run_e2e(gui, dark_mode=False)
    page.goto("/")
    page.expect_websocket()
    page.wait_for_selector("#text1")
    background_color = page.evaluate(
        'window.getComputedStyle(document.querySelector("main"), null).getPropertyValue("background-color")'
    )
    assert background_color == "rgb(255, 255, 255)"


@pytest.mark.teste2e
def test_theme_dark(page: "Page", gui: Gui, helpers):
    page_md = """
<|Just a page|id=text1|>
"""
    gui._set_frame(inspect.currentframe())
    gui.add_page(name="test", page=page_md)
    helpers.run_e2e(gui, dark_mode=True)
    page.goto("/")
    page.expect_websocket()
    page.wait_for_selector("#text1")
    background_color = page.evaluate(
        'window.getComputedStyle(document.querySelector("main"), null).getPropertyValue("background-color")'
    )
    assert background_color == "rgb(18, 18, 18)"
