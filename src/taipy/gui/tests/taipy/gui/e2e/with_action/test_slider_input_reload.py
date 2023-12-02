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


def edit_and_assert_page(page: "Page"):
    assert_input(page, "0")

    page.fill("#input2 input", "20")
    function_evaluated = True
    try:
        page.wait_for_function("document.querySelector('#val1').innerText !== '0'")
    except Exception as e:
        function_evaluated = False
        logging.getLogger().debug(f"Function evaluation timeout.\n{e}")
    if not function_evaluated:
        return
    assert_input(page, "20")

    page.fill("#input1", "30")
    function_evaluated = True
    try:
        page.wait_for_function("document.querySelector('#val1').innerText !== '20'")
        function_evaluated = True
    except Exception as e:
        function_evaluated = False
        logging.getLogger().debug(f"Function evaluation timeout.\n{e}")
    if not function_evaluated:
        return
    assert_input(page, "30")


def assert_input(page: "Page", val: str):
    val1 = page.query_selector("#val1").inner_text()
    assert str(val1).startswith(val)
    val2 = page.query_selector("#val2").inner_text()
    assert str(val2).startswith(f"Val: {val}")
    inp1 = page.input_value("input#input1")
    assert str(inp1).startswith(val)
    inp2 = page.input_value("#input2 input")
    assert str(inp2).startswith(val)


@pytest.mark.filterwarnings("ignore::Warning")
@pytest.mark.teste2e
def test_slider_input_reload(page: "Page", gui: Gui, helpers):
    page_md = """
#Test Multi Number

<|{val}|id=val1|>

<|Val: {val}|id=val2|>

<|{val}|number|id=input1|>

<|{val}|slider|id=input2|>
"""
    val = 0  # noqa: F841
    gui._set_frame(inspect.currentframe())
    gui.add_page(name="page1", page=page_md)
    helpers.run_e2e_multi_client(gui)
    page.goto("./page1")
    page.expect_websocket()
    page.wait_for_selector("#val1")
    edit_and_assert_page(page)

    page.reload()
    page.expect_websocket()
    page.wait_for_selector("#val1")
    assert_input(page, "30")

    page.evaluate("window.localStorage.removeItem('TaipyClientId')")

    page.reload()
    page.expect_websocket()
    page.wait_for_selector("#val1")
    assert_input(page, "0")
