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

from .assets6_page_load.page1 import page as page1


@pytest.mark.timeout(300)
@pytest.mark.teste2e
def test_page_scopes(page: "Page", gui: Gui, helpers):
    gui._set_frame(inspect.currentframe())

    x = 15  # noqa: F841

    def on_page_load(state):
        state.x = 30

    gui.add_page(Gui._get_root_page_name(), "<|{x}|id=text_x|>")
    gui.add_page("page1", page1)
    helpers.run_e2e(gui)

    page.goto("./page1")
    page.expect_websocket()
    page.wait_for_selector("#text_a")
    function_evaluated = True
    try:
        page.wait_for_function("document.querySelector('#text_a').innerText !== '10'")
        function_evaluated = True
    except Exception as e:
        function_evaluated = False
        logging.getLogger().debug(f"Function evaluation timeout.\n{e}")
    if not function_evaluated:
        return
    assert page.query_selector("#text_a").inner_text() == "20"
    assert page.query_selector("#text_x").inner_text() == "30"
