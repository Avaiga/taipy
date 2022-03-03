import pytest
from playwright._impl._page import Page

from taipy.gui import Gui


@pytest.mark.teste2e
def test_theme_light(page: Page, gui: Gui):
    page_md = """
<|Just a page|id=text1|>
"""
    gui.add_page(name="test", page=page_md)
    gui.run(run_in_thread=True, single_client=True, dark_mode=False)
    page.goto(url="/", wait_until="domcontentloaded")
    page.wait_for_selector("#text1")
    background_color = page.evaluate(
        'window.getComputedStyle(document.querySelector("main"), null).getPropertyValue("background-color")'
    )
    assert background_color == "rgb(255, 255, 255)"


@pytest.mark.teste2e
def test_theme_dark(page: Page, gui: Gui):
    page_md = """
<|Just a page|id=text1|>
"""
    gui.add_page(name="test", page=page_md)
    gui.run(run_in_thread=True, single_client=True, dark_mode=True)
    page.goto(url="/", wait_until="domcontentloaded")
    page.wait_for_selector("#text1")
    background_color = page.evaluate(
        'window.getComputedStyle(document.querySelector("main"), null).getPropertyValue("background-color")'
    )
    assert background_color == "rgb(18, 18, 18)"
