import pytest
from playwright._impl._page import Page

from taipy.gui import Gui


@pytest.mark.teste2e
def test_slider_action(page: Page, gui: Gui):
    page_md = """
<|{x}|id=text1|>

<|{x}|slider|id=slider1|>
"""
    x = 10
    gui.add_page(name="test", page=page_md)
    gui.run(run_in_thread=True, single_client=True)
    page.goto("/test")
    page.expect_websocket()
    page.wait_for_selector("#text1")
    text1 = page.query_selector("#text1")
    assert text1.inner_text() == "10"
    page.wait_for_selector("#slider1")
    page.fill("#slider1 input", "20")
    page.wait_for_function("document.querySelector('#text1').innerText !== '" + "10" + "'")
    assert text1.inner_text() == "20"
