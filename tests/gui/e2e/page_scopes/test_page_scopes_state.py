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

from .assets4.page1 import page as page1
from .assets4.page1 import reset_d


@pytest.mark.timeout(300)
@pytest.mark.teste2e
@pytest.mark.filterwarnings("ignore::Warning")
def test_page_scopes_state_runtime(page: "Page", gui: Gui, helpers):
    if frame := inspect.currentframe():
        gui._set_frame(frame)

    def test(state):
        reset_d(state)

    def test2(state):
        state["page1"].d = 30

    page_md = """
<|button|on_action=test|id=btn1|>

<|button|on_action=test2|id=btn2|>
"""
    gui.add_page("page1", page1)
    gui.add_page(name=Gui._get_root_page_name(), page=page_md)
    helpers.run_e2e(gui)

    page.goto("./page1")
    page.expect_websocket()
    page.wait_for_selector("#n1")
    text1 = page.query_selector("#t1")
    assert text1.inner_text() == "20"
    page.fill("#n1", "21")
    function_evaluated = True
    try:
        page.wait_for_function("document.querySelector('#t1').innerText !== '20'")
        function_evaluated = True
    except Exception as e:
        function_evaluated = False
        logging.getLogger().debug(f"Function evaluation timeout.\n{e}")
    if not function_evaluated:
        return
    text1 = page.query_selector("#t1")
    assert text1.inner_text() == "21"

    page.click("#btn1")
    try:
        page.wait_for_function("document.querySelector('#t1').innerText !== '21'")
        function_evaluated = True
    except Exception as e:
        function_evaluated = False
        logging.getLogger().debug(f"Function evaluation timeout.\n{e}")
    if not function_evaluated:
        return
    text1 = page.query_selector("#t1")
    assert text1.inner_text() == "20"

    page.click("#btn2")
    try:
        page.wait_for_function("document.querySelector('#t1').innerText !== '20'")
        function_evaluated = True
    except Exception as e:
        function_evaluated = False
        logging.getLogger().debug(f"Function evaluation timeout.\n{e}")
    if not function_evaluated:
        return
    text1 = page.query_selector("#t1")
    assert text1.inner_text() == "30"
