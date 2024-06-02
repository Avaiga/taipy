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
from importlib import util

import pytest

if util.find_spec("playwright"):
    from playwright._impl._page import Page

from taipy.gui import Gui


@pytest.mark.extension
def test_has_default_value(page: Page, gui: Gui, helpers):
    page_md = """
<|100|metric|>
"""
    gui._set_frame(inspect.currentframe())
    gui.add_page(name="test", page=page_md)
    helpers.run_e2e(gui)
    page.goto("./test")
    page.wait_for_selector(".plot-container")
    events_list = page.locator("//*[@class='js-plotly-plot']//*[name()='svg'][2]//*[local-name()='text']")
    gauge_value = events_list.nth(0).text_content()
    assert gauge_value == "100"


@pytest.mark.extension
def test_show_increase_delta_value(page: Page, gui: Gui, helpers):
    page_md = """
<|100|metric|delta=20|type=linear|>
"""
    gui._set_frame(inspect.currentframe())
    gui.add_page(name="test", page=page_md)
    helpers.run_e2e(gui)
    page.goto("./test")
    page.wait_for_selector(".plot-container")
    events_list = page.locator("//*[@class='js-plotly-plot']//*[name()='svg'][2]//*[local-name()='text']")
    delta_value = events_list.nth(1).text_content()
    assert delta_value == "▲20"


@pytest.mark.extension
def test_show_decrease_delta_value(page: Page, gui: Gui, helpers):
    page_md = """
<|100|metric|delta=-20|type=linear|>
"""
    gui._set_frame(inspect.currentframe())
    gui.add_page(name="test", page=page_md)
    helpers.run_e2e(gui)
    page.goto("./test")
    page.wait_for_selector(".plot-container")
    events_list = page.locator("//*[@class='js-plotly-plot']//*[name()='svg'][2]//*[local-name()='text']")
    delta_value = events_list.nth(1).text_content()
    assert delta_value == "▼−20"


@pytest.mark.teste2e
def test_show_linear_chart(page: Page, gui: Gui, helpers):
    page_md = """
<|100|metric|delta=-20|type=linear|>
"""
    gui._set_frame(inspect.currentframe())
    gui.add_page(name="test", page=page_md)
    helpers.run_e2e(gui)
    page.goto("./test")
    page.wait_for_selector(".plot-container")
    chart = page.locator("//*[@class='js-plotly-plot']//*[name()='svg'][2]//*[@class='bullet']")
    assert chart.is_visible()


@pytest.mark.teste2e
def test_show_circular_chart_as_default_type(page: Page, gui: Gui, helpers):
    page_md = """
<|100|metric|>
"""
    gui._set_frame(inspect.currentframe())
    gui.add_page(name="test", page=page_md)
    helpers.run_e2e(gui)
    page.goto("./test")
    page.wait_for_selector(".plot-container")
    chart = page.locator("//*[@class='js-plotly-plot']//*[name()='svg'][2]//*[@class='angular']")
    assert chart.is_visible()


@pytest.mark.teste2e
def test_format_converter_integer_to_binary(page: Page, gui: Gui, helpers):
    page_md = """
<|50|metric|show_value=True|delta=20|format=%b|>
"""
    gui._set_frame(inspect.currentframe())
    gui.add_page(name="test", page=page_md)
    helpers.run_e2e(gui)
    page.goto("./test")
    page.wait_for_selector(".plot-container")
    number = page.locator(
        "//*[@class='js-plotly-plot']//*[name()='svg'][2]//*[@class='number']")
    assert number.text_content() == "110010"


@pytest.mark.teste2e
def test_format_converter_integer_to_signed_decimal_d_type(page: Page, gui: Gui, helpers):
    page_md = """
<|50|metric|show_value=True|delta=20|format=%d|>
"""
    gui._set_frame(inspect.currentframe())
    gui.add_page(name="test", page=page_md)
    helpers.run_e2e(gui)
    page.goto("./test")
    page.wait_for_selector(".plot-container")
    number = page.locator(
        "//*[@class='js-plotly-plot']//*[name()='svg'][2]//*[@class='number']")
    assert number.text_content() == "50"


@pytest.mark.teste2e
def test_format_converter_integer_to_signed_decimal_i_type(page: Page, gui: Gui, helpers):
    page_md = """
<|50|metric|show_value=True|delta=20|format=%i|>
"""
    gui._set_frame(inspect.currentframe())
    gui.add_page(name="test", page=page_md)
    helpers.run_e2e(gui)
    page.goto("./test")
    page.wait_for_selector(".plot-container")
    number = page.locator(
        "//*[@class='js-plotly-plot']//*[name()='svg'][2]//*[@class='number']")
    assert number.text_content() == "50"


@pytest.mark.teste2e
def test_format_converter_yields_float_using_science_notation(page: Page, gui: Gui, helpers):
    page_md = """
<|50|metric|show_value=True|delta=20|format=%e|>
"""
    gui._set_frame(inspect.currentframe())
    gui.add_page(name="test", page=page_md)
    helpers.run_e2e(gui)
    page.goto("./test")
    page.wait_for_selector(".plot-container")
    number = page.locator(
        "//*[@class='js-plotly-plot']//*[name()='svg'][2]//*[@class='number']")
    assert number.text_content() == "5.000000e+1"


@pytest.mark.teste2e
def test_format_converter_yields_float_using_fixed_point_notation_f_type(page: Page, gui: Gui, helpers):
    page_md = """
<|99.99|metric|show_value=True|delta=20|format=%.2f|>
"""
    gui._set_frame(inspect.currentframe())
    gui.add_page(name="test", page=page_md)
    helpers.run_e2e(gui)
    page.goto("./test")
    page.wait_for_selector(".plot-container")
    number = page.locator(
        "//*[@class='js-plotly-plot']//*[name()='svg'][2]//*[@class='number']")
    assert number.text_content() == "99.99"


@pytest.mark.teste2e
def test_format_converter_yields_float_using_fixed_point_notation_g_type(page: Page, gui: Gui, helpers):
    page_md = """
<|50.555|metric|show_value=True|delta=20|format=%.2g|>
"""
    gui._set_frame(inspect.currentframe())
    gui.add_page(name="test", page=page_md)
    helpers.run_e2e(gui)
    page.goto("./test")
    page.wait_for_selector(".plot-container")
    number = page.locator(
        "//*[@class='js-plotly-plot']//*[name()='svg'][2]//*[@class='number']")
    assert number.text_content() == "51"


@pytest.mark.teste2e
def test_format_converter_yields_integer_as_octal(page: Page, gui: Gui, helpers):
    page_md = """
<|50|metric|show_value=True|delta=20|format=%o|>
"""
    gui._set_frame(inspect.currentframe())
    gui.add_page(name="test", page=page_md)
    helpers.run_e2e(gui)
    page.goto("./test")
    page.wait_for_selector(".plot-container")
    number = page.locator(
        "//*[@class='js-plotly-plot']//*[name()='svg'][2]//*[@class='number']")
    assert number.text_content() == "62"


@pytest.mark.teste2e
def test_format_converter_yields_integer_as_hexadecimal(page: Page, gui: Gui, helpers):
    page_md = """
<|50|metric|show_value=True|delta=20|format=%x|>
"""
    gui._set_frame(inspect.currentframe())
    gui.add_page(name="test", page=page_md)
    helpers.run_e2e(gui)
    page.goto("./test")
    page.wait_for_selector(".plot-container")
    number = page.locator(
        "//*[@class='js-plotly-plot']//*[name()='svg'][2]//*[@class='number']")
    assert number.text_content() == "32"


@pytest.mark.teste2e
def test_format_converter_yields_integer_as_uppercase_hexadecimal(page: Page, gui: Gui, helpers):
    page_md = """
<|50|metric|show_value=True|delta=20|format=%X|>
"""
    gui._set_frame(inspect.currentframe())
    gui.add_page(name="test", page=page_md)
    helpers.run_e2e(gui)
    page.goto("./test")
    page.wait_for_selector(".plot-container")
    number = page.locator(
        "//*[@class='js-plotly-plot']//*[name()='svg'][2]//*[@class='number']")
    assert number.text_content() == "32"


@pytest.mark.teste2e
def test_format_converter_yields_integer_as_unsigned_decimal(page: Page, gui: Gui, helpers):
    page_md = """
<|-50|metric|show_value=True|delta=20|format=%u|>
"""
    gui._set_frame(inspect.currentframe())
    gui.add_page(name="test", page=page_md)
    helpers.run_e2e(gui)
    page.goto("./test")
    page.wait_for_selector(".plot-container")
    number = page.locator(
        "//*[@class='js-plotly-plot']//*[name()='svg'][2]//*[@class='number']")
    assert number.text_content() == "(50)"


@pytest.mark.teste2e
def test_format_converter_yields_edge_cases(page: Page, gui: Gui, helpers):
    page_md = """
<|50|metric|show_value=True|format=a%%b%dc%%d|>
"""
    gui._set_frame(inspect.currentframe())
    gui.add_page(name="test", page=page_md)
    helpers.run_e2e(gui)
    page.goto("./test")
    page.wait_for_selector(".plot-container")
    number = page.locator(
        "//*[@class='js-plotly-plot']//*[name()='svg'][2]//*[@class='number']")
    assert number.text_content() == "a%b50c%d"



