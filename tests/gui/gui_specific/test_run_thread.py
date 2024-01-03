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
import time
from unittest.mock import patch
from urllib.request import urlopen

from taipy.gui import Gui


# this hangs in github
def test_run_thread(gui: Gui, helpers):
    if frame := inspect.currentframe():
        gui._set_frame(frame)
    gui.add_page("page1", "# first page")
    with patch("sys.argv", ["prog"]):
        gui.run(run_in_thread=True, run_browser=False)
    while not helpers.port_check():
        time.sleep(0.1)
    assert ">first page</h1>" in urlopen("http://127.0.0.1:5000/taipy-jsx/page1").read().decode("utf-8")
    gui.stop()
    while helpers.port_check():
        time.sleep(0.1)
    with patch("sys.argv", ["prog"]):
        gui.run(run_in_thread=True, run_browser=False)
    while not helpers.port_check():
        time.sleep(0.1)
    assert ">first page</h1>" in urlopen("http://127.0.0.1:5000/taipy-jsx/page1").read().decode("utf-8")
