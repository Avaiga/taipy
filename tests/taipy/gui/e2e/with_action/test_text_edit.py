from importlib import util

import pytest

if util.find_spec("playwright"):
    from playwright._impl._page import Page

from taipy.gui import Gui


@pytest.mark.teste2e
def test_text_edit(page: "Page", gui: Gui):
    page_md = """
<|{x}|text|id=text1|>

<|{x}|input|id=input1|>
"""
    x = "Hey"
    gui.add_page(name="test", page=page_md)
    gui.run(run_in_thread=True, single_client=True)
    page.goto(url="/test", wait_until="domcontentloaded", timeout=120000)
    page.wait_for_selector("#text1")
    text1 = page.query_selector("#text1")
    assert text1.inner_text() == "Hey"
    page.wait_for_selector("#input1")
    page.fill("#input1", "There")
    page.wait_for_function("document.querySelector('#text1').innerText !== '" + "Hey" + "'")
    assert text1.inner_text() == "There"


@pytest.mark.teste2e
def test_number_edit(page: "Page", gui: Gui):
    page_md = """
<|{x}|text|id=text1|>

<|{x}|number|id=number1|>

"""
    x = 10
    gui.add_page(name="test", page=page_md)
    gui.run(run_in_thread=True, single_client=True)
    page.goto(url="/test", wait_until="domcontentloaded", timeout=120000)
    page.expect_websocket()
    page.wait_for_selector("#text1")
    text1 = page.query_selector("#text1")
    assert text1.inner_text() == "10"
    page.wait_for_selector("#number1")
    page.fill("#number1", "20")
    page.wait_for_function("document.querySelector('#text1').innerText !== '" + "10" + "'")
    assert text1.inner_text() == "20"
