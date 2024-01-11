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


def test_button_md_1(gui: Gui, test_client, helpers):
    gui._bind_var_val("name", "World!")
    gui._bind_var_val("btn_id", "button1")
    md_string = "<|Hello {name}|button|id={btn_id}|>"
    expected_list = ["<Button", 'defaultLabel="Hello World!"', "label={tp_TpExPr_Hello_name_TPMDL_0_0"]
    helpers.test_control_md(gui, md_string, expected_list)


def test_button_md_2(gui: Gui, test_client, helpers):
    gui._bind_var_val("name", "World!")
    gui._bind_var_val("btn_id", "button1")
    md_string = "<|button|label=Hello {name}|id={btn_id}|>"
    expected_list = ["<Button", 'defaultLabel="Hello World!"', "label={tp_TpExPr_Hello_name_TPMDL_0_0"]
    helpers.test_control_md(gui, md_string, expected_list)


def test_button_html_1(gui: Gui, test_client, helpers):
    gui._bind_var_val("name", "World!")
    gui._bind_var_val("btn_id", "button1")
    html_string = '<taipy:button label="Hello {name}" id="{btn_id}" />'
    expected_list = ["<Button", 'defaultLabel="Hello World!"', "label={tp_TpExPr_Hello_name_TPMDL_0_0"]
    helpers.test_control_html(gui, html_string, expected_list)


def test_button_html_2(gui: Gui, test_client, helpers):
    gui._bind_var_val("name", "World!")
    gui._bind_var_val("btn_id", "button1")
    html_string = '<taipy:button id="{btn_id}">Hello {name}</taipy:button>'
    expected_list = ["<Button", 'defaultLabel="Hello World!"', "label={tp_TpExPr_Hello_name_TPMDL_0_0"]
    helpers.test_control_html(gui, html_string, expected_list)
