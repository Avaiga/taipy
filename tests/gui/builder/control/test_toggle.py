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

import taipy.gui.builder as tgb
from taipy.gui import Gui


def test_toggle_builder(gui: Gui, helpers):
    with tgb.Page(frame=None) as page:
        tgb.toggle(theme=True)  # type: ignore[attr-defined]
    expected_list = ["<Toggle", 'mode="theme"', 'unselectedValue=""']
    helpers.test_control_builder(gui, page, expected_list)


def test_toggle_allow_unselected_builder(gui: Gui, helpers):
    with tgb.Page(frame=None) as page:
        tgb.toggle(allow_unselect=True, lov="1;2")  # type: ignore[attr-defined]
    expected_list = ["<Toggle", 'unselectedValue=""', "allowUnselect={true}"]
    helpers.test_control_builder(gui, page, expected_list)


def test_toggle_lov_builder(gui: Gui, test_client, helpers):
    gui._bind_var_val("x", "l1")
    gui._bind_var_val("lov", [("l1", "v1"), ("l2", "v2")])
    with tgb.Page(frame=None) as page:
        tgb.toggle(lov="{lov}", value="{x}", label="Label")  # type: ignore[attr-defined]
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
    helpers.test_control_builder(gui, page, expected_list)
