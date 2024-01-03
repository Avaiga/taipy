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
def test_markdown_render_with_style(page: "Page", gui: Gui, helpers):
    markdown_content = """
<|Hey|id=text1|>
<|There|id=text2|class_name=custom-text|>
"""
    style = """
.taipy-text {
    color: green;
}
.custom-text {
    color: blue;
}
"""
    if frame := inspect.currentframe():
        gui._set_frame(frame)
    gui.add_page("page1", markdown_content, style=style)
    helpers.run_e2e(gui)
    page.goto("./page1")
    page.expect_websocket()
    page.wait_for_selector("#text1")
    page.wait_for_selector("#Taipy_style", state="attached")
    function_evaluated = True
    try:
        page.wait_for_function(
            'window.getComputedStyle(document.querySelector("#text1"), null).getPropertyValue("color") !== "rgb(255, 255, 255)"'  # noqa: E501
        )
    except Exception as e:
        function_evaluated = False
        logging.getLogger().debug(f"Function evaluation timeout.\n{e}")
    if function_evaluated:
        assert (
            page.evaluate('window.getComputedStyle(document.querySelector("#text1"), null).getPropertyValue("color")')
            == "rgb(0, 128, 0)"
        )
        assert (
            page.evaluate('window.getComputedStyle(document.querySelector("#text2"), null).getPropertyValue("color")')
            == "rgb(0, 0, 255)"
        )
