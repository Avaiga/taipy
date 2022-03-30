from importlib import util
import inspect

import pytest

if util.find_spec("playwright"):
    from playwright._impl._page import Page

from taipy.gui import Gui


@pytest.mark.teste2e
def test_accessor_json(page: "Page", gui: Gui, csvdata, helpers):
    table_data = csvdata
    gui._set_frame(inspect.currentframe())
    gui.add_page(
        name="test",
        page="<|{table_data}|table|page_size=10|page_size_options=10;30;100|columns=Day;Entity;Code;Daily hospital occupancy|date_format=eee dd MMM yyyy|id=table1|>",
    )
    helpers.run_e2e(gui, use_arrow=False)
    page.goto("/test")
    page.expect_websocket()
    page.wait_for_selector("#table1 tr:nth-child(32)") # wait for data to be loaded (30 rows of skeleton while loading)
    assert_table_content(page)


@pytest.mark.teste2e
def test_accessor_arrow(page: "Page", gui: Gui, csvdata, helpers):
    if util.find_spec("pyarrow"):
        table_data = csvdata
        gui._set_frame(inspect.currentframe())
        gui.add_page(
            name="test",
            page="<|{table_data}|table|page_size=10|page_size_options=10;30;100|columns=Day;Entity;Code;Daily hospital occupancy|date_format=eee dd MMM yyyy|id=table1|>",
        )
        helpers.run_e2e(gui, use_arrow=True)
        page.goto("/test")
        page.expect_websocket()
        page.wait_for_selector("#table1 tr:nth-child(32)") # wait for data to be loaded (30 rows of skeleton while loading)
        assert_table_content(page)


def assert_table_content(page: "Page"):
    assert page.query_selector("#table1 tbody tr:nth-child(1) td:nth-child(1)").inner_text() == "Wed 01 Apr 2020"
    assert page.query_selector("#table1 tbody tr:nth-child(1) td:nth-child(2)").inner_text() == "Austria"
    assert page.query_selector("#table1 tbody tr:nth-child(1) td:nth-child(4)").inner_text() == "856"
