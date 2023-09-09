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

import inspect

import taipy.gui.builder as tgb
from taipy.gui import Gui


def test_input_builder(gui: Gui, helpers):
    x = "Hello World!"  # noqa: F841
    gui._set_frame(inspect.currentframe())
    with tgb.Page(frame=None) as page:
        tgb.input(value="{x}")
    expected_list = [
        "<Input",
        'updateVarName="tpec_TpExPr_x_TPMDL_0"',
        'defaultValue="Hello World!"',
        'type="text"',
        "value={tpec_TpExPr_x_TPMDL_0}",
    ]
    helpers.test_control_builder(gui, page, expected_list)


def test_password_builder(gui: Gui, helpers):
    x = "Hello World!"  # noqa: F841
    gui._set_frame(inspect.currentframe())
    with tgb.Page(frame=None) as page:
        tgb.input(value="{x}", password=True)
    expected_list = [
        "<Input",
        'updateVarName="tpec_TpExPr_x_TPMDL_0"',
        'defaultValue="Hello World!"',
        'type="password"',
        "value={tpec_TpExPr_x_TPMDL_0}",
    ]
    helpers.test_control_builder(gui, page, expected_list)
