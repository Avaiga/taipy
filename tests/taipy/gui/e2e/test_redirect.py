import time
from importlib import util

import pytest

if util.find_spec("playwright"):
    from playwright._impl._page import Page

from taipy.gui import Gui


@pytest.mark.teste2e
def test_redirect(page: "Page", gui: Gui):
    page_md = """
<|Redirect Successfully|id=text1|>
"""
    gui.add_page(name="test", page=page_md)
    gui.run(run_in_thread=True, single_client=True)
    while not gui._server._thread.is_alive():
        time.sleep(0.2)
    page.goto(url="/", wait_until="domcontentloaded", timeout=120000)
    page.wait_for_selector("#text1")
    text1 = page.query_selector("#text1")
    assert text1.inner_text() == "Redirect Successfully"
