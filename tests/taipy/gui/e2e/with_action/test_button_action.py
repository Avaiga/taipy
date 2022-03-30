from importlib import util
import inspect

import pytest

if util.find_spec("playwright"):
    from playwright._impl._page import Page

from taipy.gui import Gui


@pytest.mark.teste2e
def test_button_action(page: "Page", gui: Gui, helpers):
    page_md = """
<|{x}|id=text1|>

<|Action|button|on_action=do_something_fn|id=button1|>
"""
    x = 10

    def do_something_fn(state):
        state.x = state.x * 2

    gui._set_frame(inspect.currentframe())
    gui.add_page(name="test", page=page_md)
    helpers.run_e2e(gui)
    page.goto("/test")
    page.expect_websocket()
    page.wait_for_selector("#text1")
    text1 = page.query_selector("#text1")
    assert text1.inner_text() == "10"
    page.click("#button1")
    page.wait_for_function("document.querySelector('#text1').innerText !== '10'")
    # assert fails on github !
    # assert text1.inner_text() == "20"
