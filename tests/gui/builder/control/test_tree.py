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


def test_tree_builder(gui: Gui, test_client, helpers):
    gui._bind_var_val("value", "Item 1")
    with tgb.Page(frame=None) as page:
        tgb.tree(value="{value}", lov="Item 1;Item 2;Item 3")  # type: ignore[attr-defined]
    expected_list = [
        "<TreeView",
        'defaultLov="[&quot;Item 1&quot;, &quot;Item 2&quot;, &quot;Item 3&quot;]"',
        'defaultValue="[&quot;Item 1&quot;]"',
        'updateVarName="_TpLv_tpec_TpExPr_value_TPMDL_0"',
        "value={_TpLv_tpec_TpExPr_value_TPMDL_0}",
    ]
    helpers.test_control_builder(gui, page, expected_list)


def test_tree_expanded_builder_1(gui: Gui, test_client, helpers):
    gui._bind_var_val("value", "Item 1")
    with tgb.Page(frame=None) as page:
        tgb.tree(value="{value}", lov="Item 1;Item 2;Item 3", expanded=False)  # type: ignore[attr-defined]
    expected_list = [
        "<TreeView",
        'defaultLov="[&quot;Item 1&quot;, &quot;Item 2&quot;, &quot;Item 3&quot;]"',
        'defaultValue="[&quot;Item 1&quot;]"',
        'updateVarName="_TpLv_tpec_TpExPr_value_TPMDL_0"',
        "value={_TpLv_tpec_TpExPr_value_TPMDL_0}",
        "expanded={false}",
    ]
    helpers.test_control_builder(gui, page, expected_list)


def test_tree_expanded_builder_2(gui: Gui, test_client, helpers):
    gui._bind_var_val("value", "Item 1")
    gui._bind_var_val("expa", ["Item1"])
    with tgb.Page(frame=None) as page:
        tgb.tree(value="{value}", lov="Item 1;Item 2;Item 3", expanded="{expa}")  # type: ignore[attr-defined]
    expected_list = [
        "<TreeView",
        'defaultLov="[&quot;Item 1&quot;, &quot;Item 2&quot;, &quot;Item 3&quot;]"',
        'defaultValue="[&quot;Item 1&quot;]"',
        'updateVarName="_TpLv_tpec_TpExPr_value_TPMDL_0"',
        "value={_TpLv_tpec_TpExPr_value_TPMDL_0}",
        'defaultExpanded="[&quot;Item1&quot;]"',
        "expanded={tpec_TpExPr_expa_TPMDL_0}",
        'updateVars="expanded=tpec_TpExPr_expa_TPMDL_0',
    ]
    helpers.test_control_builder(gui, page, expected_list)
