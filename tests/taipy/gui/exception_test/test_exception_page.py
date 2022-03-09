from email import message

import pytest

from taipy.gui._page import _Page


def test_exception_page(gui):
    page = _Page()
    page._route = "page1"
    with pytest.raises(RuntimeError, match="Can't render page page1: no renderer found"):
        page.render(gui)
