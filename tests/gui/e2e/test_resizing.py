import inspect
from importlib import util

import pandas
import pytest

if util.find_spec("playwright"):
    from playwright.sync_api import Page

from taipy.gui import Gui


@pytest.mark.teste2e
def test_has_default_value(page: "Page", gui: Gui, helpers):
    percentages = [
        (1852, 50.83),
        (1856, 45.29),
        (1860, 39.65),
        (1864, 55.03),
    ]
    data = pandas.DataFrame(percentages, columns=["Year", "%"]) # noqa: F841
    page_md = "<|{data}|chart|type=bar|x=Year|y=%|>"
    gui._set_frame(inspect.currentframe())
    gui.add_page(name="test",page=page_md)
    helpers.run_e2e(gui)
    page.goto("./test")
    page.wait_for_timeout(3000)
    plot_container = page.locator(".plot-container")
    plot_container.wait_for()
    page.set_viewport_size({"width": 800, "height": 600})
    elements = page.locator(
        'path[style*="vector-effect: non-scaling-stroke; opacity: 1; stroke-width: 0px; fill: rgb(99, 110, 250); fill-opacity: 1;"]') # noqa: E501
    first_element = elements.first
    box_before = first_element.bounding_box()
    page.set_viewport_size({"width": 1920, "height": 1080})
    page.wait_for_timeout(1000)
    box_after = first_element.bounding_box()
    assert box_after and box_before and box_after["width"] > box_before["width"]
