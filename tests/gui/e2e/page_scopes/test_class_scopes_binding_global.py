# Copyright 2021-2024 Avaiga Private Limited
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

from .assets2_class_scopes.page1 import Page1
from .assets2_class_scopes.page2 import Page2


def helpers_assert_value(page, s1, s2, v1):
    s1_val = page.input_value("#s1 input")
    assert str(s1_val).startswith(s1)
    s2_val = page.input_value("#s2 input")
    assert str(s2_val).startswith(s2)
    val1 = page.query_selector("#v1").inner_text()
    assert str(val1).startswith(v1)


@pytest.mark.timeout(300)
@pytest.mark.teste2e
@pytest.mark.filterwarnings("ignore::Warning")
def test_class_scopes_binding(page: "Page", gui: Gui, helpers):
    gui._set_frame(inspect.currentframe())
    operand_1 = 0  # noqa: F841
    gui.add_page("page1", Page1())
    gui.add_page("page2", Page2())
    helpers.run_e2e(gui)

    page.goto("./page1")
    page.expect_websocket()
    page.wait_for_selector("#s1")
    helpers_assert_value(page, "0", "0", "0")
    page.fill("#s1 input", "15")
    function_evaluated = True
    try:
        page.wait_for_function("document.querySelector('#v1').innerText !== '0'")
        function_evaluated = True
    except Exception as e:
        function_evaluated = False
        logging.getLogger().debug(f"Function evaluation timeout.\n{e}")
    if not function_evaluated:
        return
    helpers_assert_value(page, "15", "0", "15")
    page.fill("#s2 input", "20")
    function_evaluated = True
    try:
        page.wait_for_function("document.querySelector('#v1').innerText !== '15'")
        function_evaluated = True
    except Exception as e:
        function_evaluated = False
        logging.getLogger().debug(f"Function evaluation timeout.\n{e}")
    if not function_evaluated:
        return
    helpers_assert_value(page, "15", "20", "35")

    page.goto("./page2")
    page.expect_websocket()
    page.wait_for_selector("#s1")
    helpers_assert_value(page, "15", "0", "0")
    page.fill("#s2 input", "5")
    function_evaluated = True
    try:
        page.wait_for_function("document.querySelector('#v1').innerText !== '0'")
        function_evaluated = True
    except Exception as e:
        function_evaluated = False
        logging.getLogger().debug(f"Function evaluation timeout.\n{e}")
    if not function_evaluated:
        return
    helpers_assert_value(page, "15", "5", "75")
    page.fill("#s1 input", "17")
    function_evaluated = True
    try:
        page.wait_for_function("document.querySelector('#v1').innerText !== '75'")
        function_evaluated = True
    except Exception as e:
        function_evaluated = False
        logging.getLogger().debug(f"Function evaluation timeout.\n{e}")
    if not function_evaluated:
        return
    helpers_assert_value(page, "17", "5", "85")

    page.goto("./page1")
    page.expect_websocket()
    page.wait_for_selector("#s1")
    helpers_assert_value(page, "17", "20", "37")

    page.click("#btn_reset")
    try:
        page.wait_for_function("document.querySelector('#v1').innerText !== '37'")
        function_evaluated = True
    except Exception as e:
        function_evaluated = False
        logging.getLogger().debug(f"Function evaluation timeout.\n{e}")
    if not function_evaluated:
        return
    helpers_assert_value(page, "17", "0", "17")
