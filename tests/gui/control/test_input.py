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

import inspect

from taipy.gui import Gui


def test_input_md(gui: Gui, helpers):
    x = "Hello World!"  # noqa: F841
    gui._set_frame(inspect.currentframe())
    md_string = "<|{x}|input|>"
    expected_list = [
        "<Input",
        'updateVarName="tpec_TpExPr_x_TPMDL_0"',
        'defaultValue="Hello World!"',
        'type="text"',
        "value={tpec_TpExPr_x_TPMDL_0}",
    ]
    helpers.test_control_md(gui, md_string, expected_list)


def test_input_md_width(gui: Gui, helpers):
    x = "Hello World!"  # noqa: F841
    gui._set_frame(inspect.currentframe())
    md_string = "<|{x}|input|width=70%|>"
    expected_list = [
        "<Input",
        'updateVarName="tpec_TpExPr_x_TPMDL_0"',
        'defaultValue="Hello World!"',
        'type="text"',
        'width="70%"',
        "value={tpec_TpExPr_x_TPMDL_0}",
    ]
    helpers.test_control_md(gui, md_string, expected_list)


def test_password_md(gui: Gui, helpers):
    x = "Hello World!"  # noqa: F841
    gui._set_frame(inspect.currentframe())
    md_string = "<|{x}|input|password|>"
    expected_list = [
        "<Input",
        'updateVarName="tpec_TpExPr_x_TPMDL_0"',
        'defaultValue="Hello World!"',
        'type="password"',
        "value={tpec_TpExPr_x_TPMDL_0}",
    ]
    helpers.test_control_md(gui, md_string, expected_list)


def test_input_html_1(gui: Gui, helpers):
    x = "Hello World!"  # noqa: F841
    gui._set_frame(inspect.currentframe())
    html_string = '<taipy:input value="{x}" />'
    expected_list = [
        "<Input",
        'updateVarName="tpec_TpExPr_x_TPMDL_0"',
        'defaultValue="Hello World!"',
        'type="text"',
        "value={tpec_TpExPr_x_TPMDL_0}",
    ]
    helpers.test_control_html(gui, html_string, expected_list)


def test_password_html(gui: Gui, helpers):
    x = "Hello World!"  # noqa: F841
    gui._set_frame(inspect.currentframe())
    html_string = '<taipy:input value="{x}" password="True" width="{100}" />'
    expected_list = [
        "<Input",
        'updateVarName="tpec_TpExPr_x_TPMDL_0"',
        'defaultValue="Hello World!"',
        'type="password"',
        'width={100}',
        "value={tpec_TpExPr_x_TPMDL_0}",
    ]
    helpers.test_control_html(gui, html_string, expected_list)


def test_input_html_2(gui: Gui, helpers):
    x = "Hello World!"  # noqa: F841
    gui._set_frame(inspect.currentframe())
    html_string = "<taipy:input>{x}</taipy:input>"
    expected_list = [
        "<Input",
        'updateVarName="tpec_TpExPr_x_TPMDL_0"',
        'defaultValue="Hello World!"',
        'type="text"',
        "value={tpec_TpExPr_x_TPMDL_0}",
    ]
    helpers.test_control_html(gui, html_string, expected_list)
