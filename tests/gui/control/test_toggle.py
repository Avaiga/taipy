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


def test_toggle_md(gui: Gui, helpers):
    md_string = "<|toggle|theme|>"
    expected_list = ["<Toggle", 'mode="theme"', 'unselectedValue=""']
    helpers.test_control_md(gui, md_string, expected_list)


def test_toggle_width_md(gui: Gui, helpers):
    md_string = "<|toggle|theme|width=70%|>"
    expected_list = ["<Toggle", 'mode="theme"', 'unselectedValue=""', 'width="70%"']
    helpers.test_control_md(gui, md_string, expected_list)


def test_toggle_allow_unselected_md(gui: Gui, helpers):
    md_string = "<|toggle|lov=1;2|allow_unselect|>"
    expected_list = ["<Toggle", 'unselectedValue=""', "allowUnselect={true}"]
    helpers.test_control_md(gui, md_string, expected_list)


def test_toggle_lov_md(gui: Gui, test_client, helpers):
    gui._bind_var_val("x", "l1")
    gui._bind_var_val("lov", [("l1", "v1"), ("l2", "v2")])
    md_string = "<|{x}|toggle|lov={lov}|label=Label|>"
    expected_list = [
        "<Toggle",
        'defaultLov="[[&quot;l1&quot;, &quot;v1&quot;], [&quot;l2&quot;, &quot;v2&quot;]]"',
        'defaultValue="l1"',
        'label="Label"',
        "lov={_TpL_tp_TpExPr_gui_get_adapted_lov_lov_tuple_TPMDL_0_0}",
        'updateVars="lov=_TpL_tp_TpExPr_gui_get_adapted_lov_lov_tuple_TPMDL_0_0"',
        'updateVarName="_TpLv_tpec_TpExPr_x_TPMDL_0"',
        'unselectedValue=""',
        "value={_TpLv_tpec_TpExPr_x_TPMDL_0}",
    ]
    helpers.test_control_md(gui, md_string, expected_list)


def test_toggle_html_1(gui: Gui, helpers):
    html_string = '<taipy:toggle theme="True" />'
    expected_list = ["<Toggle", 'mode="theme"', 'unselectedValue=""']
    helpers.test_control_html(gui, html_string, expected_list)


def test_toggle_html_2(gui: Gui, test_client, helpers):
    gui._bind_var_val("x", "l1")
    gui._bind_var_val("lov", [("l1", "v1"), ("l2", "v2")])
    html_string = '<taipy:toggle lov="{lov}" label="Label">{x}</taipy:toggle>'
    expected_list = [
        "<Toggle",
        'defaultLov="[[&quot;l1&quot;, &quot;v1&quot;], [&quot;l2&quot;, &quot;v2&quot;]]"',
        'defaultValue="l1"',
        'label="Label"',
        "lov={_TpL_tp_TpExPr_gui_get_adapted_lov_lov_tuple_TPMDL_0_0}",
        'updateVars="lov=_TpL_tp_TpExPr_gui_get_adapted_lov_lov_tuple_TPMDL_0_0"',
        'updateVarName="_TpLv_tpec_TpExPr_x_TPMDL_0"',
        'unselectedValue=""',
        "value={_TpLv_tpec_TpExPr_x_TPMDL_0}",
    ]
    helpers.test_control_html(gui, html_string, expected_list)


def test_toggle_switch_md(gui: Gui, test_client, helpers):
    gui._bind_var_val("x", True)
    md_string = "<|{x}|toggle|label=Label|>"
    expected_list = [
        "<Toggle",
        "isSwitch={true}",
        "defaultValue={true}",
        'libClassName="taipy-toggle"',
        'updateVarName="_TpB_tpec_TpExPr_x_TPMDL_0"',
        "value={_TpB_tpec_TpExPr_x_TPMDL_0}",
        'label="Label"',
    ]
    helpers.test_control_md(gui, md_string, expected_list)
