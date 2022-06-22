# Copyright 2022 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import time
from urllib.request import urlopen

import pytest
from testbook import testbook


@pytest.mark.filterwarnings("ignore::RuntimeWarning")
@testbook("tests/taipy/gui/notebook/simple_gui.ipynb")
def test_notebook_simple_gui(tb, helpers):
    tb.execute_cell("import")
    tb.execute_cell("page_declaration")
    tb.execute_cell("gui_init")
    tb.execute_cell("gui_run")
    while not helpers.port_check():
        time.sleep(0.1)
    assert ">Hello</h1>" in urlopen("http://127.0.0.1:5000/taipy-jsx/page1").read().decode("utf-8")
    tb.execute_cell("gui_stop")
    assert helpers.port_check() is False
    tb.execute_cell("gui_re_run")
    while not helpers.port_check():
        time.sleep(0.1)
    assert ">Hello</h1>" in urlopen("http://127.0.0.1:5000/taipy-jsx/page1").read().decode("utf-8")
    tb.execute_cell("gui_re_stop")
    assert helpers.port_check() is False
