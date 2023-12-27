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
import re
from importlib import util

import pytest

if util.find_spec("playwright"):
    from playwright._impl._page import Page
    from playwright.sync_api import expect

from taipy.gui import Gui


@pytest.mark.teste2e
def test_navbar_navigate(page: "Page", gui: Gui, helpers):
    if frame := inspect.currentframe():
        gui._set_frame(frame)
    gui.add_page(name="Data", page="<|navbar|id=nav1|> <|Data|id=text-data|>")
    gui.add_page(name="Test", page="<|navbar|id=nav1|> <|Test|id=text-test|>")
    helpers.run_e2e(gui)
    page.goto("./Data")
    page.expect_websocket()
    page.wait_for_selector("#text-data")
    page.click("#nav1 button:nth-child(2)")
    page.wait_for_selector("#text-test")
    expect(page).to_have_url(re.compile(".*Test"))
    page.click("#nav1 button:nth-child(1)")
    page.wait_for_selector("#text-data")
    expect(page).to_have_url(re.compile(".*Data"))
