import pytest
from playwright._impl._page import Page

from taipy.gui import Gui
from taipy.gui.utils.date import ISO_to_date


@pytest.mark.teste2e
def test_timzone_specified_1(page: Page, gui: Gui):
    _timezone_test_template(page, gui, "Etc/GMT", "2022-03-03 00:00:00 UTC")


@pytest.mark.teste2e
def test_timzone_specified_2(page: Page, gui: Gui):
    _timezone_test_template(page, gui, "Europe/Paris", "2022-03-03 01:00:00 GMT+1")


@pytest.mark.teste2e
def test_timzone_specified_3(page: Page, gui: Gui):
    _timezone_test_template(page, gui, "Asia/Ho_Chi_Minh", "2022-03-03 07:00:00 GMT+7")


@pytest.mark.teste2e
def test_timzone_specified_4(page: Page, gui: Gui):
    _timezone_test_template(page, gui, "America/Sao_Paulo", "2022-03-02 21:00:00 GMT-3")


@pytest.mark.teste2e
def test_timezone_client_side(page: Page, gui: Gui):
    _timezone_test_template(page, gui, "client", "2022-03-03 01:00:00 GMT+1")


def _timezone_test_template(page: Page, gui: Gui, time_zone, text):
    page_md = """
<|{time}|id=text1|>
"""
    time = ISO_to_date("2022-03-03T00:00:00.000Z")
    gui.add_page(name="test", page=page_md)
    gui.run(run_in_thread=True, single_client=True, time_zone=time_zone)
    page.goto("/test")
    page.expect_websocket()
    page.wait_for_selector("#text1")
    text1 = page.query_selector("#text1")
    assert text1.inner_text() == text
