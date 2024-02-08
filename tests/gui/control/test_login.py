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


def test_login_md(gui: Gui, test_client, helpers):
    md_string = "<|login|on_action=on_login_action|>"
    expected_list = [
        "<Login",
        'libClassName="taipy-login"',
        'onAction="on_login_action"',
    ]
    helpers.test_control_md(gui, md_string, expected_list)


def test_login_html(gui: Gui, test_client, helpers):
    html_string = '<taipy:login on_action="on_login_action" />'
    expected_list = [
        "<Login",
        'libClassName="taipy-login"',
        'onAction="on_login_action"',
    ]
    helpers.test_control_html(gui, html_string, expected_list)
