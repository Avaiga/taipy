# Copyright 2021-2025 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import contextlib
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

import pytest
from testbook import testbook

from taipy.gui import Gui


def wait_for_content(url, expected_text, timeout=10):
    start = time.time()
    while time.time() - start < timeout:
        try:
            response = urlopen(url)
            content = response.read().decode("utf-8")
            if expected_text in content:
                return True
        except (HTTPError, URLError):
            pass
        time.sleep(0.5)
    return False


@pytest.mark.skip_if_not_server("flask")
@pytest.mark.skipif(sys.platform.startswith("win"), reason="Test skipped on Windows")
@pytest.mark.filterwarnings("ignore::RuntimeWarning")
@pytest.mark.teste2e
@testbook("tests/gui/notebook/simple_gui.ipynb")
def test_notebook_simple_gui(tb, helpers):
    tb.execute_cell("import")
    tb.execute_cell("page_declaration")
    tb.execute_cell("gui_init")
    tb.execute_cell("gui_run")
    while not helpers.port_check():
        time.sleep(0.1)
    assert wait_for_content(f"http://127.0.0.1:5000/{Gui._JSX_URL}/page1", ">Hello</h1>"), "Expected content not found"
    assert 'defaultValue=\\"10\\"' in urlopen(f"http://127.0.0.1:5000/{Gui._JSX_URL}/page1").read().decode("utf-8")
    # Test state manipulation within notebook
    tb.execute_cell("get_variable")
    assert "10" in tb.cell_output_text("get_variable")
    assert 'defaultValue=\\"10\\"' in urlopen(f"http://127.0.0.1:5000/{Gui._JSX_URL}/page1").read().decode("utf-8")
    tb.execute_cell("set_variable")
    assert 'defaultValue=\\"20\\"' in urlopen(f"http://127.0.0.1:5000/{Gui._JSX_URL}/page1").read().decode("utf-8")
    tb.execute_cell("re_get_variable")
    assert "20" in tb.cell_output_text("re_get_variable")
    # Test page reload
    tb.execute_cell("gui_stop")
    with pytest.raises(Exception) as exc_info:
        urlopen(f"http://127.0.0.1:5000/{Gui._JSX_URL}/page1")
    assert "501: Gateway error" in str(exc_info.value)
    tb.execute_cell("gui_re_run")
    while True:
        with contextlib.suppress(Exception):
            urlopen(f"http://127.0.0.1:5000/{Gui._JSX_URL}/page1")
            break
    assert wait_for_content(f"http://127.0.0.1:5000/{Gui._JSX_URL}/page1", ">Hello</h1>"), "Expected content not found"
    tb.execute_cell("gui_reload")
    while True:
        with contextlib.suppress(Exception):
            urlopen(f"http://127.0.0.1:5000/{Gui._JSX_URL}/page1")
            break
    assert wait_for_content(f"http://127.0.0.1:5000/{Gui._JSX_URL}/page1", ">Hello</h1>"), "Expected content not found"
    tb.execute_cell("gui_re_stop")
    with pytest.raises(Exception) as exc_info:
        urlopen(f"http://127.0.0.1:5000/{Gui._JSX_URL}/page1")
    assert "501: Gateway error" in str(exc_info.value)


@pytest.mark.skip_if_not_server("fastapi")
@pytest.mark.filterwarnings("ignore::RuntimeWarning")
@pytest.mark.teste2e
@testbook("tests/gui/notebook/simple_gui_fastapi.ipynb")
def test_notebook_simple_gui_fastapi(tb, helpers):
    tb.execute_cell("import")
    tb.execute_cell("page_declaration")
    tb.execute_cell("gui_init")
    tb.execute_cell("gui_run")
    while not helpers.port_check():
        time.sleep(0.1)
    assert wait_for_content(f"http://127.0.0.1:5000/{Gui._JSX_URL}/page1", ">Hello</h1>"), "Expected content not found"
    assert 'defaultValue=\\"10\\"' in urlopen(f"http://127.0.0.1:5000/{Gui._JSX_URL}/page1").read().decode("utf-8")
    # Test state manipulation within notebook
    tb.execute_cell("get_variable")
    assert "10" in tb.cell_output_text("get_variable")
    assert 'defaultValue=\\"10\\"' in urlopen(f"http://127.0.0.1:5000/{Gui._JSX_URL}/page1").read().decode("utf-8")
    tb.execute_cell("set_variable")
    assert 'defaultValue=\\"20\\"' in urlopen(f"http://127.0.0.1:5000/{Gui._JSX_URL}/page1").read().decode("utf-8")
    tb.execute_cell("re_get_variable")
    assert "20" in tb.cell_output_text("re_get_variable")
    # Test page reload
    tb.execute_cell("gui_stop")
    with pytest.raises(Exception) as exc_info:
        urlopen(f"http://127.0.0.1:5000/{Gui._JSX_URL}/page1")
    assert "refused" in str(exc_info.value)
    tb.execute_cell("gui_re_run")
    while True:
        with contextlib.suppress(Exception):
            urlopen(f"http://127.0.0.1:5000/{Gui._JSX_URL}/page1")
            break
    assert wait_for_content(f"http://127.0.0.1:5000/{Gui._JSX_URL}/page1", ">Hello</h1>"), "Expected content not found"
    tb.execute_cell("gui_reload")
    while True:
        with contextlib.suppress(Exception):
            urlopen(f"http://127.0.0.1:5000/{Gui._JSX_URL}/page1")
            break
    assert wait_for_content(f"http://127.0.0.1:5000/{Gui._JSX_URL}/page1", ">Hello</h1>"), "Expected content not found"
    tb.execute_cell("gui_re_stop")
    with pytest.raises(Exception) as exc_info:
        urlopen(f"http://127.0.0.1:5000/{Gui._JSX_URL}/page1")
    assert "refused" in str(exc_info.value)
