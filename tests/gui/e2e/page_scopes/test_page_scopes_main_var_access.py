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

from taipy.gui import Gui, Markdown

if util.find_spec("playwright"):
    from playwright._impl._page import Page

from .assets3.page1 import page as page1


def helpers_assert_text(page, s):
    val1 = page.query_selector("#t1").inner_text()
    assert str(val1).startswith(s)


# for issue #583
@pytest.mark.teste2e
@pytest.mark.filterwarnings("ignore::Warning")
def test_page_scopes_main_var_access(page: "Page", gui: Gui, helpers):
    if frame := inspect.currentframe():
        gui._set_frame(frame)
    n = "Hello"  # noqa: F841

    root_md = Markdown(
        """

<|{n}|input|id=i1|>

"""
    )
    gui.add_pages({"/": root_md, "page1": page1})
    helpers.run_e2e(gui)

    page.goto("./")
    page.expect_websocket()
    page.wait_for_selector("#t1")
    page.wait_for_selector("#i1")
    helpers_assert_text(page, "Hello")
    page.fill("#i1", "Hello World")
    function_evaluated = True
    try:
        page.wait_for_function("document.querySelector('#t1').innerText !== 'Hello'")
        function_evaluated = True
    except Exception as e:
        function_evaluated = False
        logging.getLogger().debug(f"Function evaluation timeout.\n{e}")
    if not function_evaluated:
        return
    helpers_assert_text(page, "Hello World")
