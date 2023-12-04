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

import contextlib
import time
from urllib.request import urlopen

import pytest
from testbook import testbook


@pytest.mark.filterwarnings("ignore::RuntimeWarning")
@testbook("tests/gui/notebook/simple_gui.ipynb")
def test_notebook_simple_gui(tb, helpers):
    tb.execute_cell("import")
    tb.execute_cell("page_declaration")
    tb.execute_cell("gui_init")
    tb.execute_cell("gui_run")
    while not helpers.port_check():
        time.sleep(0.1)
    assert ">Hello</h1>" in urlopen("http://127.0.0.1:5000/taipy-jsx/page1").read().decode("utf-8")
    assert 'defaultValue=\\"10\\"' in urlopen("http://127.0.0.1:5000/taipy-jsx/page1").read().decode("utf-8")
    # Test state manipulation within notebook
    tb.execute_cell("get_variable")
    assert "10" in tb.cell_output_text("get_variable")
    assert 'defaultValue=\\"10\\"' in urlopen("http://127.0.0.1:5000/taipy-jsx/page1").read().decode("utf-8")
    tb.execute_cell("set_variable")
    assert 'defaultValue=\\"20\\"' in urlopen("http://127.0.0.1:5000/taipy-jsx/page1").read().decode("utf-8")
    tb.execute_cell("re_get_variable")
    assert "20" in tb.cell_output_text("re_get_variable")
    # Test page reload
    tb.execute_cell("gui_stop")
    with pytest.raises(Exception) as exc_info:
        urlopen("http://127.0.0.1:5000/taipy-jsx/page1")
    assert "501: Gateway error" in str(exc_info.value)
    tb.execute_cell("gui_re_run")
    while True:
        with contextlib.suppress(Exception):
            urlopen("http://127.0.0.1:5000/taipy-jsx/page1")
            break
    assert ">Hello</h1>" in urlopen("http://127.0.0.1:5000/taipy-jsx/page1").read().decode("utf-8")
    tb.execute_cell("gui_reload")
    while True:
        with contextlib.suppress(Exception):
            urlopen("http://127.0.0.1:5000/taipy-jsx/page1")
            break
    assert ">Hello</h1>" in urlopen("http://127.0.0.1:5000/taipy-jsx/page1").read().decode("utf-8")
    tb.execute_cell("gui_re_stop")
    with pytest.raises(Exception) as exc_info:
        urlopen("http://127.0.0.1:5000/taipy-jsx/page1")
    assert "501: Gateway error" in str(exc_info.value)
