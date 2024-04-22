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


def test_menu_builder(gui: Gui, test_client, helpers):
    gui._bind_var_val("lov", ["Item 1", "Item 2", "Item 3", "Item 4"])
    with tgb.Page(frame=None) as page:
        tgb.menu(lov="{lov}", on_action="on_menu_action")  # type: ignore[attr-defined]
    expected_list = [
        "<MenuCtl",
        'libClassName="taipy-menu"',
        'defaultLov="[&quot;Item 1&quot;, &quot;Item 2&quot;, &quot;Item 3&quot;, &quot;Item 4&quot;]"',
        "lov={_TpL_tp_TpExPr_gui_get_adapted_lov_lov_tuple_TPMDL_0_0}",
        'onAction="on_menu_action"',
        'updateVars="lov=_TpL_tp_TpExPr_gui_get_adapted_lov_lov_tuple_TPMDL_0_0"',
    ]
    helpers.test_control_builder(gui, page, expected_list)
