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

from .another_module import exported_page


def test_lambda_1(gui: Gui, test_client, helpers):
    md_string = "<|Hello|button|on_action={lambda s,i,p: None}|>"
    expected_list = ['onAction="__lambda_', "_TPMDL_1"]
    helpers.test_control_md(gui, md_string, expected_list)

def test_lambda_2(gui: Gui, test_client, helpers):
    expected_list = ['onAction="__lambda_', "_TPMDL_1"]
    gui.add_page("test", exported_page)
    helpers._test_control(gui, expected_list)
