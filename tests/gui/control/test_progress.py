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

from taipy.gui import Gui
from tests.gui.helpers import Helpers


def test_circular_progress_indeterminate_md(gui: Gui, helpers: type[Helpers]):
    md_string = "<|progress|>"
    expected_list = ["<Progress"]
    helpers.test_control_md(gui, md_string, expected_list)


def test_circular_progress_determinate_md(gui: Gui, helpers: type[Helpers]):
    md_string = "<|progress|value=50|showValue=True|>"
    expected_list = ["<Progress", 'value="50"']
    helpers.test_control_md(gui, md_string, expected_list)


def test_linear_progress_indeterminate_md(gui: Gui, helpers: Helpers):
    md_string = "<|progress|linear=True|>"
    expected_list = ["<Progress", "linear"]
    helpers.test_control_md(gui, md_string, expected_list)


def test_linear_progress_determinate_md(gui: Gui, helpers: Helpers):
    md_string = "<|progress|value=50|showValue=True|linear=True|>"
    expected_list = ["<Progress", 'value="50"', "linear"]
    helpers.test_control_md(gui, md_string, expected_list)


def test_circular_progress_indeterminate_html(gui: Gui, helpers: Helpers):
    html_string = "<taipy:progress></taipy:progress>"
    expected_list = ["<Progress"]
    helpers.test_control_html(gui, html_string, expected_list)


def test_circular_progress_determinate_html(gui: Gui, helpers: Helpers):
    html_string = '<taipy:progress showValue=True value="50"></taipy:progress>'
    expected_list = ["<Progress", 'value="50"']
    helpers.test_control_html(gui, html_string, expected_list)


def test_linear_progress_indeterminate_html(gui: Gui, helpers: Helpers):
    html_string = "<taipy:progress linear=True></taipy:progress>"
    expected_list = ["<Progress", "linear"]
    helpers.test_control_html(gui, html_string, expected_list)


def test_linear_progress_determinate_html(gui: Gui, helpers: Helpers):
    html_string = '<taipy:progress linear=True showValue=True value="50"></taipy:progress>'
    expected_list = ["<Progress", "linear", 'value="50"']
    helpers.test_control_html(gui, html_string, expected_list)
