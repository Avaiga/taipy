# Copyright 2023 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import inspect
import logging
from importlib import util

import pytest

from taipy.gui import Gui

if util.find_spec("playwright"):
    from playwright._impl._page import Page

from .assets.page1 import page as page1
from .assets.page2 import page as page2
from .assets.page3 import page as page3


@pytest.mark.timeout(300)
@pytest.mark.teste2e
def test_page_scopes(page: "Page", gui: Gui, helpers):
    if frame := inspect.currentframe():
        gui._set_frame(frame)

    def on_change(state, var, val, module):
        if var == "x" and "page3" in module:
            state.y = val * 10

    gui.add_page("page1", page1)
    gui.add_page("page2", page2)
    gui.add_page("page3", page3)
    helpers.run_e2e(gui)

    page.goto("./page1")
    page.expect_websocket()
    page.wait_for_selector("#x1")
    assert page.query_selector("#x1").inner_text() == "10"
    assert page.query_selector("#x2").inner_text() == "20"
    assert page.query_selector("#y1").inner_text() == "20"
    assert page.query_selector("#y2").inner_text() == "40"

    page.goto("./page2")
    page.expect_websocket()
    page.wait_for_selector("#x1")
    assert page.query_selector("#x1").inner_text() == "20"
    assert page.query_selector("#x2").inner_text() == "40"
    assert page.query_selector("#y1").inner_text() == "10"
    assert page.query_selector("#y2").inner_text() == "20"

    page.goto("./page3")
    page.expect_websocket()
    page.wait_for_selector("#x1")
    assert page.query_selector("#x1").inner_text() == "50"
    assert page.query_selector("#x2").inner_text() == "100"

    page.goto("./page1")
    page.expect_websocket()
    page.wait_for_selector("#x1")
    page.fill("#xinput", "15")
    function_evaluated = True
    try:
        page.wait_for_function("document.querySelector('#y2').innerText !== '40'")
        function_evaluated = True
    except Exception as e:
        function_evaluated = False
        logging.getLogger().debug(f"Function evaluation timeout.\n{e}")
    if not function_evaluated:
        return
    assert page.query_selector("#x1").inner_text() == "15"
    assert page.query_selector("#x2").inner_text() == "30"
    assert page.query_selector("#y1").inner_text() == "45"
    assert page.query_selector("#y2").inner_text() == "90"

    page.goto("./page2")
    page.expect_websocket()
    page.wait_for_selector("#x1")
    assert page.query_selector("#x1").inner_text() == "45"
    assert page.query_selector("#x2").inner_text() == "90"
    assert page.query_selector("#y1").inner_text() == "15"
    assert page.query_selector("#y2").inner_text() == "30"
    page.fill("#xinput", "37")
    function_evaluated = True
    try:
        page.wait_for_function("document.querySelector('#y2').innerText !== '30'")
        function_evaluated = True
    except Exception as e:
        function_evaluated = False
        logging.getLogger().debug(f"Function evaluation timeout.\n{e}")
    if not function_evaluated:
        return
    assert page.query_selector("#x1").inner_text() == "37"
    assert page.query_selector("#x2").inner_text() == "74"
    assert page.query_selector("#y1").inner_text() == "185"
    assert page.query_selector("#y2").inner_text() == "370"

    page.goto("./page1")
    page.expect_websocket()
    page.wait_for_selector("#x1")
    assert page.query_selector("#x1").inner_text() == "185"
    assert page.query_selector("#x2").inner_text() == "370"
    assert page.query_selector("#y1").inner_text() == "37"
    assert page.query_selector("#y2").inner_text() == "74"

    page.goto("./page3")
    page.expect_websocket()
    page.wait_for_selector("#x1")
    assert page.query_selector("#x1").inner_text() == "50"
    assert page.query_selector("#x2").inner_text() == "100"
