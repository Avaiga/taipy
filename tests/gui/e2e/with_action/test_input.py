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
def test_input_action(page: "Page", gui: Gui, helpers):
    page_md = """
<|{input1_value}|input|on_action=input_action|id=input1|>
<|{input2_value}|input|on_action=input_action|id=input2|action_on_blur|>
<|X|button|id=button1|on_action=button_action|>
<|{input1_action_tracker}|id=input1_tracker|>
<|{input2_action_tracker}|id=input2_tracker|>
<|{button_action_tracker}|id=button_tracker|>
"""
    input1_value = "init"  # noqa: F841
    input2_value = "init"  # noqa: F841
    input1_action_tracker = 0  # noqa: F841
    input2_action_tracker = 0  # noqa: F841
    button_action_tracker = 0  # noqa: F841

    def input_action(state, id):
        if id == "input1":
            state.input1_action_tracker = state.input1_action_tracker + 1
        elif id == "input2":
            state.input2_action_tracker = state.input2_action_tracker + 1

    def button_action(state, id):
        state.button_action_tracker = state.button_action_tracker + 1

    gui._set_frame(inspect.currentframe())
    gui.add_page(name="test", page=page_md)
    helpers.run_e2e(gui)
    page.goto("./test")
    page.expect_websocket()
    page.wait_for_selector("#input1_tracker")
    assert page.query_selector("#input1").input_value() == "init", "Wrong initial value"
    page.click("#button1")
    try:
        page.wait_for_function("document.querySelector('#button_tracker').innerText !== '0'")
    except Exception as e:
        logging.getLogger().debug(f"Function evaluation timeout.\n{e}")
    assert page.query_selector("#button_tracker").inner_text() == "1"
    page.click("#input1")
    page.fill("#input1", "step2")
    page.click("#button1")
    try:
        page.wait_for_function("document.querySelector('#button_tracker').innerText !== '1'")
    except Exception as e:
        logging.getLogger().debug(f"Function evaluation timeout.\n{e}")
    assert page.query_selector("#button_tracker").inner_text() == "2", "Button action should have been invoked"
    assert (
        page.query_selector("#input1_tracker").inner_text() == "0"
    ), "Action should not have been invoked (no action_on_blur)"
    page.click("#input2")
    page.fill("#input2", "step2")
    page.click("#button1")
    try:
        page.wait_for_function("document.querySelector('#button_tracker').innerText !== '2'")
    except Exception as e:
        logging.getLogger().debug(f"Function evaluation timeout.\n{e}")
    assert page.query_selector("#button_tracker").inner_text() == "3", "Button action should have been invoked"
    assert (
        page.query_selector("#input2_tracker").inner_text() == "1"
    ), "Action should have been invoked (action_on_blur)"
