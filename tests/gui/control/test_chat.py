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

from taipy.gui import Gui, Icon


def test_chat_md_1(gui: Gui, test_client, helpers):
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
        {
            "users": [
                ["Fred", Icon("/images/favicon.png", "Fred.png")],
                ["Fredi", Icon("/images/fred.png", "Fred.png")],
            ],
            "sender_id": "sender",
            "on_action": "on_action",
            "with_input": False,
            "height": "50vh"
        },
    )
    md_string = "<|{messages}|chat|properties=chat_properties|>"
    expected_list = [
        "<Chat",
        'defaultUsers="[[&quot;Fred&quot;, &#x7B;&quot;path&quot;: &quot;/images/favicon.png&quot;, &quot;text&quot;: &quot;Fred.png&quot;&#x7D;], [&quot;Fredi&quot;, &#x7B;&quot;path&quot;: &quot;/images/fred.png&quot;, &quot;text&quot;: &quot;Fred.png&quot;&#x7D;]]"',  # noqa: E501
        "messages={tpec_TpExPr_messages_TPMDL_0}",
        'updateVarName="tpec_TpExPr_messages_TPMDL_0"',
        'senderId="sender"',
        'onAction="on_action"',
        "defaultWithInput={false}",
        'height="50vh"'
    ]
    helpers.test_control_md(gui, md_string, expected_list)


def test_chat_md_2(gui: Gui, test_client, helpers):
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
    gui._bind_var_val("winp", False)
    md_string = "<|{messages}|chat|users={users}|with_input={winp}|>"
    expected_list = [
        "<Chat",
        'defaultUsers="[[&quot;Fred&quot;, &#x7B;&quot;path&quot;: &quot;/images/favicon.png&quot;, &quot;text&quot;: &quot;Fred.png&quot;&#x7D;], [&quot;Fredi&quot;, &#x7B;&quot;path&quot;: &quot;/images/fred.png&quot;, &quot;text&quot;: &quot;Fred.png&quot;&#x7D;]]"',  # noqa: E501
        "messages={tpec_TpExPr_messages_TPMDL_0}",
        'updateVarName="tpec_TpExPr_messages_TPMDL_0"',
        "users={_TpL_tpec_TpExPr_users_TPMDL_0}",
        'updateVars="users=_TpL_tpec_TpExPr_users_TPMDL_0"',
        "withInput={_TpB_tpec_TpExPr_winp_TPMDL_0}",
        "defaultWithInput={false}"
    ]
    helpers.test_control_md(gui, md_string, expected_list)


def test_chat_html_1_1(gui: Gui, test_client, helpers):
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
    html_string = '<taipy:chat messages="{messages}" properties="chat_properties"/>'
    expected_list = [
        "<Chat",
        'defaultUsers="[[&quot;Fred&quot;, &#x7B;&quot;path&quot;: &quot;/images/favicon.png&quot;, &quot;text&quot;: &quot;Fred.png&quot;&#x7D;], [&quot;Fredi&quot;, &#x7B;&quot;path&quot;: &quot;/images/fred.png&quot;, &quot;text&quot;: &quot;Fred.png&quot;&#x7D;]]"',  # noqa: E501
        "messages={tpec_TpExPr_messages_TPMDL_0}",
        'updateVarName="tpec_TpExPr_messages_TPMDL_0"',
    ]
    helpers.test_control_html(gui, html_string, expected_list)


def test_chat_html_1_2(gui: Gui, test_client, helpers):
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
    html_string = '<taipy:chat properties="chat_properties">{messages}</taipy:chat>'
    expected_list = [
        "<Chat",
        'defaultUsers="[[&quot;Fred&quot;, &#x7B;&quot;path&quot;: &quot;/images/favicon.png&quot;, &quot;text&quot;: &quot;Fred.png&quot;&#x7D;], [&quot;Fredi&quot;, &#x7B;&quot;path&quot;: &quot;/images/fred.png&quot;, &quot;text&quot;: &quot;Fred.png&quot;&#x7D;]]"',  # noqa: E501
        "messages={tpec_TpExPr_messages_TPMDL_0}",
        'updateVarName="tpec_TpExPr_messages_TPMDL_0"',
    ]
    helpers.test_control_html(gui, html_string, expected_list)


def test_chat_html_2_1(gui: Gui, test_client, helpers):
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
    html_string = '<taipy:chat messages="{messages}" users="{users}" />'
    expected_list = [
        "<Chat",
        'defaultUsers="[[&quot;Fred&quot;, &#x7B;&quot;path&quot;: &quot;/images/favicon.png&quot;, &quot;text&quot;: &quot;Fred.png&quot;&#x7D;], [&quot;Fredi&quot;, &#x7B;&quot;path&quot;: &quot;/images/fred.png&quot;, &quot;text&quot;: &quot;Fred.png&quot;&#x7D;]]"',  # noqa: E501
        "messages={tpec_TpExPr_messages_TPMDL_0}",
        'updateVarName="tpec_TpExPr_messages_TPMDL_0"',
        "users={_TpL_tpec_TpExPr_users_TPMDL_0}",
        'updateVars="users=_TpL_tpec_TpExPr_users_TPMDL_0"',
    ]
    helpers.test_control_html(gui, html_string, expected_list)


def test_chat_html_2_2(gui: Gui, test_client, helpers):
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
    html_string = '<taipy:chat users="{users}">{messages}</taipy:chat>'
    expected_list = [
        "<Chat",
        'defaultUsers="[[&quot;Fred&quot;, &#x7B;&quot;path&quot;: &quot;/images/favicon.png&quot;, &quot;text&quot;: &quot;Fred.png&quot;&#x7D;], [&quot;Fredi&quot;, &#x7B;&quot;path&quot;: &quot;/images/fred.png&quot;, &quot;text&quot;: &quot;Fred.png&quot;&#x7D;]]"',  # noqa: E501
        "messages={tpec_TpExPr_messages_TPMDL_0}",
        'updateVarName="tpec_TpExPr_messages_TPMDL_0"',
        "users={_TpL_tpec_TpExPr_users_TPMDL_0}",
        'updateVars="users=_TpL_tpec_TpExPr_users_TPMDL_0"',
    ]
    helpers.test_control_html(gui, html_string, expected_list)
