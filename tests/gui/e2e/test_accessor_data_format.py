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
def test_accessor_json(page: "Page", gui: Gui, csvdata, helpers):
    table_data = csvdata  # noqa: F841
    gui._set_frame(inspect.currentframe())
    gui.add_page(
        name="test",
        page="<|{table_data}|table|columns=Day;Entity;Code;Daily hospital occupancy|date_format=eee dd MMM yyyy|id=table1|>",  # noqa: E501
    )
    helpers.run_e2e(gui, use_arrow=False)
    page.goto("./test")
    page.expect_websocket()
    page.wait_for_selector("#table1 tr:nth-child(32)")  # wait for data to be loaded (30 rows of skeleton while loading)
    assert_table_content(page)


@pytest.mark.teste2e
def test_accessor_arrow(page: "Page", gui: Gui, csvdata, helpers):
    if util.find_spec("pyarrow"):
        table_data = csvdata  # noqa: F841
        gui._set_frame(inspect.currentframe())
        gui.add_page(
            name="test",
            page="<|{table_data}|table|columns=Day;Entity;Code;Daily hospital occupancy|date_format=eee dd MMM yyyy|id=table1|>",  # noqa: E501
        )
        helpers.run_e2e(gui, use_arrow=True)
        page.goto("./test")
        page.expect_websocket()
        page.wait_for_selector(
            "#table1 tr:nth-child(32)"
        )  # wait for data to be loaded (30 rows of skeleton while loading)
        assert_table_content(page)


def assert_table_content(page: "Page"):
    # assert page.query_selector("#table1 tbody tr:nth-child(1) td:nth-child(1)").inner_text() == "Wed 01 Apr 2020"
    assert page.query_selector("#table1 tbody tr:nth-child(1) td:nth-child(2)").inner_text() == "Austria"
    assert page.query_selector("#table1 tbody tr:nth-child(1) td:nth-child(4)").inner_text() == "856"
