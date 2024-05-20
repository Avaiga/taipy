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
from taipy.gui import Gui, Icon


def test_chat_builder_1(gui: Gui, test_client, helpers):
    gui._bind_var_val(
        "messages",
        [
            ["1", "msg 1", "Fred"],
            ["2", "msg From Another unknown User", "Fredo"],
            ["3", "This from the sender User", "taipy"],
            ["4", "And from another known one", "Fredi"],
        ],
    )

    gui._bind_var_val(
        "chat_properties",
        {"users": [["Fred", Icon("/images/favicon.png", "Fred.png")], ["Fredi", Icon("/images/fred.png", "Fred.png")]]},
    )

    with tgb.Page(frame=None) as page:
        tgb.chat(messages="{messages}", properties="{chat_properties}")  # type: ignore[attr-defined]
    expected_list = [
        "<Chat",
        'defaultUsers="[[&quot;Fred&quot;, &#x7B;&quot;path&quot;: &quot;/images/favicon.png&quot;, &quot;text&quot;: &quot;Fred.png&quot;&#x7D;], [&quot;Fredi&quot;, &#x7B;&quot;path&quot;: &quot;/images/fred.png&quot;, &quot;text&quot;: &quot;Fred.png&quot;&#x7D;]]"',  # noqa: E501
        "messages={_TpD_tpec_TpExPr_messages_TPMDL_0}",
        "updateVarName=\"_TpD_tpec_TpExPr_messages_TPMDL_0\""
    ]
    helpers.test_control_builder(gui, page, expected_list)


def test_chat_builder_2(gui: Gui, test_client, helpers):
    gui._bind_var_val(
        "messages",
        [
            ["1", "msg 1", "Fred"],
            ["2", "msg From Another unknown User", "Fredo"],
            ["3", "This from the sender User", "taipy"],
            ["4", "And from another known one", "Fredi"],
        ],
    )

    gui._bind_var_val(
        "users", [["Fred", Icon("/images/favicon.png", "Fred.png")], ["Fredi", Icon("/images/fred.png", "Fred.png")]]
    )

    with tgb.Page(frame=None) as page:
        tgb.chat(messages="{messages}", users="{users}")  # type: ignore[attr-defined]
    expected_list = [
        "<Chat",
        'defaultUsers="[[&quot;Fred&quot;, &#x7B;&quot;path&quot;: &quot;/images/favicon.png&quot;, &quot;text&quot;: &quot;Fred.png&quot;&#x7D;], [&quot;Fredi&quot;, &#x7B;&quot;path&quot;: &quot;/images/fred.png&quot;, &quot;text&quot;: &quot;Fred.png&quot;&#x7D;]]"',  # noqa: E501
        "messages={_TpD_tpec_TpExPr_messages_TPMDL_0}",
        "updateVarName=\"_TpD_tpec_TpExPr_messages_TPMDL_0\"",
        "users={_TpL_tp_TpExPr_gui_get_adapted_lov_users_list_TPMDL_0_0}",
        "updateVars=\"users=_TpL_tp_TpExPr_gui_get_adapted_lov_users_list_TPMDL_0_0\""
    ]
    helpers.test_control_builder(gui, page, expected_list)
