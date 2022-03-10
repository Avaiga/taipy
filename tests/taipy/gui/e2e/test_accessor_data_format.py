import time
from importlib import util

import pytest

if util.find_spec("playwright"):
    from playwright._impl._page import Page

from taipy.gui import Gui


@pytest.mark.teste2e
def test_accessor_json(page: "Page", gui: Gui, csvdata, helpers):
    table_data = csvdata
    gui.add_page(
        name="test",
        page="<|{table_data}|table|page_size=10|page_size_options=10;30;100|columns=Day;Entity;Code;Daily hospital occupancy|date_format=eee dd MMM yyyy|id=table1|>",
    )
    gui.run(run_in_thread=True, single_client=True, use_arrow=False)
    while not helpers.port_check():
        time.sleep(0.1)
    page.goto("/test")
    page.expect_websocket()
    page.wait_for_selector("#table1")
    assert_table_content(page)


@pytest.mark.teste2e
def test_accessor_arrow(page: "Page", gui: Gui, csvdata, helpers):
    if util.find_spec("pyarrow"):
        table_data = csvdata
        gui.add_page(
            name="test",
            page="<|{table_data}|table|page_size=10|page_size_options=10;30;100|columns=Day;Entity;Code;Daily hospital occupancy|date_format=eee dd MMM yyyy|id=table1|>",
        )
        gui.run(run_in_thread=True, single_client=True, use_arrow=True)
        while not helpers.port_check():
            time.sleep(0.1)
        page.goto("/test")
        page.expect_websocket()
        page.wait_for_selector("#table1")
        assert_table_content(page)


def assert_table_content(page: "Page"):
    assert page.query_selector("#table1 tbody tr:nth-child(1) td:nth-child(1)").inner_text() == "Wed 01 Apr 2020"
    assert page.query_selector("#table1 tbody tr:nth-child(1) td:nth-child(2)").inner_text() == "Austria"
    assert page.query_selector("#table1 tbody tr:nth-child(1) td:nth-child(4)").inner_text() == "856"
