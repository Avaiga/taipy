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

from .assets5_import_all.page1 import page as page1


def helpers_assert_value(page, numa, numb):
    assert page.query_selector("#num_a").inner_text() == numa
    assert page.query_selector("#num_b").inner_text() == numb

@pytest.mark.timeout(300)
@pytest.mark.teste2e
@pytest.mark.filterwarnings("ignore::Warning")
def test_page_scopes_import_all(page: "Page", gui: Gui, helpers):
    gui._set_frame(inspect.currentframe())
    gui.add_page("page1", page1)
    helpers.run_e2e(gui)

    page.goto("./page1")
    page.expect_websocket()
    page.wait_for_selector("#num_a")
    helpers_assert_value(page, "10", "20")
    page.click("#btn_a")
    function_evaluated = True
    try:
        page.wait_for_function("document.querySelector('#num_a').innerText !== '10'")
        function_evaluated = True
    except Exception as e:
        function_evaluated = False
        logging.getLogger().debug(f"Function evaluation timeout.\n{e}")
    if not function_evaluated:
        return
    helpers_assert_value(page, "20", "20")
    page.click("#btn_b")
    function_evaluated = True
    try:
        page.wait_for_function("document.querySelector('#num_b').innerText !== '20'")
        function_evaluated = True
    except Exception as e:
        function_evaluated = False
        logging.getLogger().debug(f"Function evaluation timeout.\n{e}")
    if not function_evaluated:
        return
    helpers_assert_value(page, "20", "40")
