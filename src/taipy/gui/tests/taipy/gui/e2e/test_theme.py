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
from importlib import util

import pytest

if util.find_spec("playwright"):
    from playwright._impl._page import Page

from taipy.gui import Gui


@pytest.mark.teste2e
def test_theme_light(page: "Page", gui: Gui, helpers):
    page_md = """
<|Just a page|id=text1|>
"""
    gui._set_frame(inspect.currentframe())
    gui.add_page(name="test", page=page_md)
    helpers.run_e2e(gui, dark_mode=False)
    page.goto("./")
    page.expect_websocket()
    page.wait_for_selector("#text1")
    background_color = page.evaluate(
        'window.getComputedStyle(document.querySelector("main"), null).getPropertyValue("background-color")'
    )
    assert background_color == "rgb(255, 255, 255)"


@pytest.mark.teste2e
def test_theme_dark(page: "Page", gui: Gui, helpers):
    page_md = """
<|Just a page|id=text1|>
"""
    gui._set_frame(inspect.currentframe())
    gui.add_page(name="test", page=page_md)
    helpers.run_e2e(gui, dark_mode=True)
    page.goto("./")
    page.expect_websocket()
    page.wait_for_selector("#text1")
    background_color = page.evaluate(
        'window.getComputedStyle(document.querySelector("main"), null).getPropertyValue("background-color")'
    )
    assert background_color == "rgb(18, 18, 18)"
