import time

import pytest
from playwright._impl._page import Page

from taipy.gui import Gui


@pytest.mark.teste2e
def test_slider_action(page: Page, gui: Gui):
    page_md = """
<|{x}|selector|lov=Item 1;Item 2;Item 3|id=selector1|>
"""
    x = "Item 1"
    gui.add_page(name="test", page=page_md)
    gui.run(run_in_thread=True, single_client=True)
    page.goto(url="/test", wait_until="domcontentloaded", timeout=120000)
    page.expect_websocket()
    page.wait_for_selector("#selector1")
    assert gui._bindings().x == "Item 1"
    page.click('#selector1 ul > div[data-id="Item 3"]')
    time.sleep(1)
    assert gui._bindings().x == "Item 3"
