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
import time
from importlib import util

import pytest

if util.find_spec("playwright"):
    from playwright._impl._page import Page

from taipy.gui import Gui, State


@pytest.mark.teste2e
def test_selector_action(page: "Page", gui: Gui, helpers):
    page_md = """
<|{x}|selector|lov=Item 1;Item 2;Item 3|id=selector1|>
"""
    x = "Item 1"  # noqa: F841

    def on_init(state: State):
        assert state.x == "Item 1"

    def on_change(state: State, var, val):
        if var == "x":
            assert val == "Item 3"

    gui._set_frame(inspect.currentframe())
    gui.add_page(name="test", page=page_md)
    helpers.run_e2e(gui)
    page.goto("./test")
    page.expect_websocket()
    page.wait_for_selector("ul#selector1")
    page.click('#selector1 > div[data-id="Item 3"]')
    page.wait_for_function(
        "document.querySelector('#selector1 > div[data-id=\"Item 3\"]').classList.contains('Mui-selected')"
    )
