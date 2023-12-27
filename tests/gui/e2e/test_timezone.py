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
from taipy.gui.utils.date import _string_to_date


@pytest.mark.teste2e
def test_timzone_specified_1(page: "Page", gui: Gui, helpers):
    _timezone_test_template(page, gui, helpers, "Etc/GMT", ["2022-03-03 00:00:00 UTC"])


@pytest.mark.teste2e
def test_timzone_specified_2(page: "Page", gui: Gui, helpers):
    _timezone_test_template(
        page, gui, helpers, "Europe/Paris", ["2022-03-03 01:00:00 GMT+1", "2022-03-03 01:00:00 UTC+1"]
    )


@pytest.mark.teste2e
def test_timzone_specified_3(page: "Page", gui: Gui, helpers):
    _timezone_test_template(
        page, gui, helpers, "Asia/Ho_Chi_Minh", ["2022-03-03 07:00:00 GMT+7", "2022-03-03 07:00:00 UTC+7"]
    )


@pytest.mark.teste2e
def test_timzone_specified_4(page: "Page", gui: Gui, helpers):
    _timezone_test_template(
        page, gui, helpers, "America/Sao_Paulo", ["2022-03-02 21:00:00 GMT-3", "2022-03-02 21:00:00 UTC−3"]
    )


@pytest.mark.teste2e
def test_timezone_client_side(page: "Page", gui: Gui, helpers):
    _timezone_test_template(page, gui, helpers, "client", ["2022-03-03 01:00:00 GMT+1", "2022-03-03 01:00:00 UTC+1"])


def _timezone_test_template(page: "Page", gui: Gui, helpers, time_zone, texts):
    page_md = """
<|{t}|id=text1|>
"""
    t = _string_to_date("2022-03-03T00:00:00.000Z")  # noqa: F841
    if frame := inspect.currentframe():
        gui._set_frame(frame)
    gui.add_page(name="test", page=page_md)
    helpers.run_e2e(gui, time_zone=time_zone)
    page.goto("./test")
    page.expect_websocket()
    page.wait_for_selector("#text1")
    text1 = page.query_selector("#text1")
    assert text1.inner_text() in texts


def test_date_only(page: "Page", gui: Gui, helpers):
    page_md = """
<|{t}|id=text1|>
"""
    t = _string_to_date("Wed Jul 28 1993")  # noqa: F841
    if frame := inspect.currentframe():
        gui._set_frame(frame)
    gui.add_page(name="test", page=page_md)
    helpers.run_e2e(gui)
    page.goto("./test")
    page.expect_websocket()
    page.wait_for_selector("#text1")
    text1 = page.query_selector("#text1")
    assert text1.inner_text() in ["1993-07-28"]
