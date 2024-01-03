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
import typing as t
from pathlib import Path

import pytest

from taipy.gui import Gui
from taipy.gui.extension import Element, ElementLibrary, ElementProperty, PropertyType


def render_xhtml_4_my_library(properties: t.Dict[str, t.Any]) -> str:
    return f"<h1>{properties.get('value', '')}</h1>"


def render_xhtml_4_my_library_fail(properties: t.Dict[str, t.Any]) -> str:
    return f"<h1>{properties.get('value', '')}</h1"


class MyLibrary(ElementLibrary):
    elts = {
        "testinput": Element(
            "value",
            {
                "value": ElementProperty(PropertyType.dynamic_string, "Fred"),
                "multiline": ElementProperty(PropertyType.boolean, False),
                "broadcast": ElementProperty(PropertyType.broadcast, "broadcast"),
            },
            "Input",
        ),
        "title": Element(
            "value",
            {
                "value": ElementProperty(PropertyType.string, ""),
            },
            "h1",
            render_xhtml=render_xhtml_4_my_library,
        ),
        "title_fail": Element(
            "value",
            {
                "value": ElementProperty(PropertyType.string, ""),
            },
            "h1",
            render_xhtml=render_xhtml_4_my_library_fail,
        ),
        "inner": Element(
            "value",
            {"value": ElementProperty(PropertyType.string, "")},
            inner_properties={
                "with_property": ElementProperty(
                    PropertyType.react,
                    "{<tp:prop:value>}",
                ),
            },
        ),
    }

    def get_name(self) -> str:
        return "test_lib"

    def get_elements(self) -> t.Dict[str, Element]:
        return MyLibrary.elts

    def get_resource(self, name: str) -> Path:
        return Path(name)


class MyBadLibrary(ElementLibrary):
    def get_name(self) -> str:
        return "bad name"

    def get_elements(self) -> t.Dict[str, Element]:
        return {}


class MyGoodLibrary(ElementLibrary):
    def get_name(self) -> str:
        return "test_lib"

    def get_elements(self) -> t.Dict[str, Element]:
        return {}


Gui.add_library(MyLibrary())


def test_lib_input_md(gui: Gui, test_client, helpers):
    val = ""  # noqa: F841
    if frame := inspect.currentframe():
        gui._set_frame(frame)
    md_string = "<|{val}|test_lib.testinput|multiline|>"
    expected_list = [
        "<TestLib_Input",
        'libClassName="test_lib-testinput"',
        "multiline={true}",
        'defaultValue=""',
        "broadcast={_bc_broadcast}",
        "value={tpec_TpExPr_val_TPMDL_0}",
    ]
    helpers.test_control_md(gui, md_string, expected_list)


def test_lib_xhtml_md(gui: Gui, test_client, helpers):
    val = "title"  # noqa: F841
    if frame := inspect.currentframe():
        gui._set_frame(frame)
    md_string = "<|{val}|test_lib.title|>"
    expected = [f"<h1>{val}</h1>"]
    helpers.test_control_md(gui, md_string, expected)


def test_lib_xhtml_fail_md(gui: Gui, test_client, helpers):
    val = "title"  # noqa: F841
    if frame := inspect.currentframe():
        gui._set_frame(frame)
    md_string = "<|{val}|test_lib.title_fail|>"
    expected = ["title_fail.render_xhtml() did not return a valid XHTML string. unclosed token: line 1, column 9"]
    helpers.test_control_md(gui, md_string, expected)


def test_lib_input_html_1(gui: Gui, test_client, helpers):
    val = ""  # noqa: F841
    if frame := inspect.currentframe():
        gui._set_frame(frame)
    html_string = '<test_lib:testinput value="{val}" multiline="true" />'
    expected_list = [
        "<TestLib_Input",
        "multiline={true}",
        'defaultValue=""',
        "broadcast={_bc_broadcast}",
        "value={tpec_TpExPr_val_TPMDL_0}",
        "</TestLib_Input>",
    ]
    helpers.test_control_html(gui, html_string, expected_list)


def test_lib_input_html_2(gui: Gui, test_client, helpers):
    val = ""  # noqa: F841
    if frame := inspect.currentframe():
        gui._set_frame(frame)
    html_string = '<test_lib:testinput multiline="true">{val}</test_lib:testinput>'
    expected_list = [
        "<TestLib_Input",
        "multiline={true}",
        'defaultValue=""',
        "broadcast={_bc_broadcast}",
        "value={tpec_TpExPr_val_TPMDL_0}",
        "</TestLib_Input>",
    ]
    helpers.test_control_html(gui, html_string, expected_list)


def test_lib_inner_md(gui: Gui, test_client, helpers):
    val = "title"  # noqa: F841
    if frame := inspect.currentframe():
        gui._set_frame(frame)
    md_string = "<|{val}|test_lib.inner|>"
    expected = [
        "<TestLib_Inner",
        "value={tpec_TpExPr_val_TPMDL_0}",
        "withProperty={tpec_TpExPr_tpec_TpExPr_val_TPMDL_0_TPMDL_0}",
    ]
    helpers.test_control_md(gui, md_string, expected)


def test_lib_inner_no_value_md(gui: Gui, test_client, helpers):
    if frame := inspect.currentframe():
        gui._set_frame(frame)
    md_string = "<|test_lib.inner|>"
    expected = ["<TestLib_Inner", "withProperty={tpec_TpExPr_None_TPMDL_0}"]
    helpers.test_control_md(gui, md_string, expected)


def test_lib_bad_name():
    with pytest.raises(NameError):
        Gui.add_library(MyBadLibrary())


def test_lib_good_name():
    Gui.add_library(MyGoodLibrary())


def test_add_lib():
    Gui(libraries=[MyGoodLibrary()])
