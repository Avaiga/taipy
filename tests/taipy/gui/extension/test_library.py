# Copyright 2022 Avaiga Private Limited
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
import typing as t
from pathlib import Path

from taipy.gui import Gui
from taipy.gui.extension import Element, ElementAttribute, ElementLibrary, PropertyType


class MyLibrary(ElementLibrary):

    elts = [
        Element(
            "testinput",
            "value",
            [
                ElementAttribute("value", PropertyType.dynamic_string, "Fred"),
                ElementAttribute("multiline", PropertyType.boolean, False),
            ],
            "Input",
        )
    ]

    def get_name(self) -> str:
        return "testlib"

    def get_elements(self) -> t.List[Element]:
        return MyLibrary.elts

    def get_scripts(self) -> t.List[str]:
        return []

    def get_styles(self) -> t.List[str]:
        return None

    def get_resource(self, name: str) -> Path:
        return None


Gui.add_library(MyLibrary())


def test_lib_input_md(gui: Gui, test_client, helpers):
    val = ""  # noqa: F841
    gui._set_frame(inspect.currentframe())
    md_string = "<|{val}|testlib.testinput|multiline|>"
    expected_list = [
        "<Input",
        'className="testlib-testinput"',
        "multiline={true}",
        'defaultValue=""',
        "value={tpec_TpExPr_val_TPMDL_0}",
    ]
    helpers.test_control_md(gui, md_string, expected_list)


def test_lib_input_html_1(gui: Gui, test_client, helpers):
    val = ""
    gui._set_frame(inspect.currentframe())
    html_string = '<testlib:testinput value="{val}" multiline="true" />'
    expected_list = ["<Input", "multiline={true}", 'defaultValue=""', "value={tpec_TpExPr_val_TPMDL_0}"]
    helpers.test_control_html(gui, html_string, expected_list)


def test_lib_input_html_2(gui: Gui, test_client, helpers):
    val = ""
    gui._set_frame(inspect.currentframe())
    html_string = '<testlib:testinput multiline="true">{val}</testlib:testinput>'
    expected_list = ["<Input", "multiline={true}", 'defaultValue=""', "value={tpec_TpExPr_val_TPMDL_0}"]
    helpers.test_control_html(gui, html_string, expected_list)
