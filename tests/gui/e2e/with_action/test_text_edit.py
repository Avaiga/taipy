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

if util.find_spec("playwright"):
    from playwright._impl._page import Page

from taipy.gui import Gui


@pytest.mark.teste2e
def test_text_edit(page: "Page", gui: Gui, helpers):
    page_md = """
<|{x}|text|id=text1|>

<|{x}|input|id=input1|>
"""
    x = "Hey"  # noqa: F841
    gui._set_frame(inspect.currentframe())
    gui.add_page(name="test", page=page_md)
    helpers.run_e2e(gui)
    page.goto("./test")
    page.expect_websocket()
    page.wait_for_selector("#text1")
    text1 = page.query_selector("#text1")
    assert text1.inner_text() == "Hey"
    page.wait_for_selector("#input1")
    page.fill("#input1", "There")
    function_evaluated = True
    try:
        page.wait_for_function("document.querySelector('#text1').innerText !== 'Hey'")
    except Exception as e:
        function_evaluated = False
        logging.getLogger().debug(f"Function evaluation timeout.\n{e}")
    if function_evaluated:
        text1_2 = page.query_selector("#text1")
        assert text1_2.inner_text() == "There"


@pytest.mark.teste2e
def test_number_edit(page: "Page", gui: Gui, helpers):
    page_md = """
<|{x}|text|id=text1|>

<|{x}|number|id=number1|>

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
    page.wait_for_selector("#number1")
    page.fill("#number1", "20")
    function_evaluated = True
    try:
        page.wait_for_function("document.querySelector('#text1').innerText !== '10'")
        function_evaluated = True
    except Exception as e:
        function_evaluated = False
        logging.getLogger().debug(f"Function evaluation timeout.\n{e}")
    if function_evaluated:
        text1_2 = page.query_selector("#text1")
        assert text1_2.inner_text() == "20"
