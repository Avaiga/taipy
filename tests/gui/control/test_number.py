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


def test_number_md_1(gui: Gui, helpers):
    md_string = "<|10|number|>"
    expected_list = ["<Input", 'value="10"', 'type="number"']
    helpers.test_control_md(gui, md_string, expected_list)


def test_number_md_2(gui: Gui, test_client, helpers):
    gui._bind_var_val("x", "10")
    md_string = "<|{x}|number|>"
    expected_list = [
        "<Input",
        'updateVarName="_TpN_tpec_TpExPr_x_TPMDL_0"',
        'defaultValue="10"',
        'type="number"',
        "value={_TpN_tpec_TpExPr_x_TPMDL_0}",
    ]
    helpers.test_control_md(gui, md_string, expected_list)


def test_number_md_width(gui: Gui, helpers):
    md_string = "<|10|number|width=70%|>"
    expected_list = ["<Input", 'value="10"', 'type="number"', 'width="70%"']
    helpers.test_control_md(gui, md_string, expected_list)


def test_number_html_1(gui: Gui, test_client, helpers):
    gui._bind_var_val("x", 10)
    html_string = '<taipy:number value="{x}" />'
    expected_list = [
        "<Input",
        'updateVarName="_TpN_tpec_TpExPr_x_TPMDL_0"',
        'defaultValue="10"',
        'type="number"',
        "value={_TpN_tpec_TpExPr_x_TPMDL_0}",
    ]
    helpers.test_control_html(gui, html_string, expected_list)


def test_number_html_2(gui: Gui, test_client, helpers):
    gui._bind_var_val("x", 10)
    html_string = "<taipy:number>{x}</taipy:number>"
    expected_list = [
        "<Input",
        'updateVarName="_TpN_tpec_TpExPr_x_TPMDL_0"',
        'defaultValue="10"',
        'type="number"',
        "value={_TpN_tpec_TpExPr_x_TPMDL_0}",
    ]
    helpers.test_control_html(gui, html_string, expected_list)
