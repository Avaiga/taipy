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


def test_builder_lambda(gui: Gui, test_client, helpers):
    message = {"a": "value A", "b": "value B"}
    gui._bind_var_val("message", message)
    with tgb.Page(frame=None) as page:
        for key in message:
            tgb.text(lambda message: str(message.get(key)))  # type: ignore[attr-defined] # noqa: B023
    expected_list = ['defaultValue="value A"', 'defaultValue="value B"']
    helpers.test_control_builder(gui, page, expected_list)


def test_builder_lambda_2(gui: Gui, test_client, helpers):
    message = {"a": "value A", "b": "value B"}
    gui._bind_var_val("message", message)
    with tgb.Page(frame=None) as page:
        for key in message:
            tgb.text(lambda message: str(message.get(key)), mode=lambda message: "mode " + str(message.get(key)))  # type: ignore[attr-defined] # noqa: B023
    expected_list = ['defaultValue="value A"', 'defaultValue="value B"', 'mode="mode value A"', 'mode="mode value B"']
    helpers.test_control_builder(gui, page, expected_list)

def test_builder_lambda_f_string(gui: Gui, test_client, helpers):
    value = 10
    gui._bind_var_val("value", value)
    with tgb.Page(frame=None) as page:
        tgb.text(lambda value: f"value is {value}")  # type: ignore[attr-defined] # noqa: B023
    expected_list = ['defaultValue="value is 10"']
    helpers.test_control_builder(gui, page, expected_list)

def test_builder_simple_lambda(gui: Gui, test_client, helpers):
    value = 10
    gui._bind_var_val("value", value)
    with tgb.Page(frame=None) as page:
        tgb.text(lambda value: value)  # type: ignore[attr-defined] # noqa: B023
    expected_list = ['defaultValue="10"']
    helpers.test_control_builder(gui, page, expected_list)

def test_builder_multiline_lambda(gui: Gui, test_client, helpers):
    value = 10
    gui._bind_var_val("value", value)
    with tgb.Page(frame=None) as page:
        tgb.text(  # type: ignore[attr-defined] # noqa: B023
            lambda value: value)
    expected_list = ['defaultValue="10"']
    helpers.test_control_builder(gui, page, expected_list)
