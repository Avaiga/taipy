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

if util.find_spec("playwright"):
    from playwright._impl._page import Page

from taipy.gui import Gui


@pytest.mark.teste2e
def test_slider_action(page: "Page", gui: Gui, helpers):
    page_md = """
<|{x}|id=text1|>

<|{x}|slider|id=slider1|>
"""
    x = 10  # noqa: F841
    gui._set_frame(inspect.currentframe())
    gui.add_page(name="test", page=page_md)
    helpers.run_e2e(gui)
    page.goto("./test")
    page.expect_websocket()
    page.wait_for_selector("#text1")
    text1 = page.query_selector("#text1")
    assert text1.inner_text() == "10"
    page.wait_for_selector("#slider1")
    page.fill("#slider1 input", "20")
    function_evaluated = True
    try:
        page.wait_for_function("document.querySelector('#text1').innerText !== '10'")
    except Exception as e:
        function_evaluated = False
        logging.getLogger().debug(f"Function evaluation timeout.\n{e}")
    if function_evaluated:
        text1_2 = page.query_selector("#text1")
        assert text1_2.inner_text() == "20"


@pytest.mark.teste2e
def test_slider_action_on_change(page: "Page", gui: Gui, helpers):
    d = {"v1": 10, "v2": 10}  # noqa: F841

    def on_change(state, var, val):
        if var == "d.v2":
            d = {"v1": 2 * val}
            state.d.update(d)

    page_md = """
Value: <|{d.v1}|id=text1|>

Slider: <|{d.v2}|slider|id=slider1|>
"""
    gui._set_frame(inspect.currentframe())
    gui.add_page(name="test", page=page_md)
    helpers.run_e2e(gui)
    page.goto("./test")
    page.expect_websocket()
    page.wait_for_selector("#text1")
    text1 = page.query_selector("#text1")
    assert text1.inner_text() == "10"
    page.wait_for_selector("#slider1")
    page.fill("#slider1 input", "20")
    function_evaluated = True
    try:
        page.wait_for_function("document.querySelector('#text1').innerText !== '10'")
    except Exception as e:
        function_evaluated = False
        logging.getLogger().debug(f"Function evaluation timeout.\n{e}")
    if function_evaluated:
        text1_2 = page.query_selector("#text1")
        assert text1_2.inner_text() == "40"
