# Copyright 2023 Avaiga Private Limited
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

import taipy.gui.builder as tgb
from taipy.gui import Gui


def test_slider_builder(gui: Gui, test_client, helpers):
    gui._bind_var_val("x", 10)
    with tgb.Page(frame=None) as page:
        tgb.slider(value="{x}")  # type: ignore[attr-defined]
    expected_list = [
        "<Slider",
        'updateVarName="_TpN_tpec_TpExPr_x_TPMDL_0',
        "defaultValue={10}",
        "value={_TpN_tpec_TpExPr_x_TPMDL_0}",
    ]
    helpers.test_control_builder(gui, page, expected_list)


def test_slider_with_min_max_builder(gui: Gui, test_client, helpers):
    gui._bind_var_val("x", 0)
    with tgb.Page(frame=None) as page:
        tgb.slider(value="{x}", min=-10, max=10)  # type: ignore[attr-defined]
    expected_list = ["<Slider", "min={-10.0}", "max={10.0}", "defaultValue={0}"]
    helpers.test_control_builder(gui, page, expected_list)


def test_slider_with_dict_labels_builder(gui: Gui, helpers):
    sel = "Item 1"  # noqa: F841
    labels = {"Item 1": "Label Start", "Item 3": "Label End"}  # noqa: F841
    if frame := inspect.currentframe():
        gui._set_frame(frame)
    with tgb.Page(frame=None) as page:
        tgb.slider(value="{sel}", lov="Item 1;Item 2;Item 3", labels=labels)  # type: ignore[attr-defined]
    expected_list = [
        "<Slider",
        'labels="{&quot;Item 1&quot;: &quot;Label Start&quot;, &quot;Item 3&quot;: &quot;Label End&quot;}"',
    ]
    helpers.test_control_builder(gui, page, expected_list)


def test_slider_with_boolean_labels_builder(gui: Gui, helpers):
    sel = "Item 1"  # noqa: F841
    if frame := inspect.currentframe():
        gui._set_frame(frame)
    with tgb.Page(frame=None) as page:
        tgb.slider(value="{sel}", lov="Item 1;Item 2;Item 3", labels=True)  # type: ignore[attr-defined]
    expected_list = ["<Slider", "labels={true}"]
    helpers.test_control_builder(gui, page, expected_list)


def test_slider_items_builder(gui: Gui, test_client, helpers):
    gui._bind_var_val("x", "Item 1")
    with tgb.Page(frame=None) as page:
        tgb.slider(value="{x}", lov="Item 1;Item 2;Item 3", text_anchor="left")  # type: ignore[attr-defined]
    expected_list = [
        "<Slider",
        'updateVarName="_TpLv_tpec_TpExPr_x_TPMDL_0"',
        "value={_TpLv_tpec_TpExPr_x_TPMDL_0}",
        'defaultLov="[&quot;Item 1&quot;, &quot;Item 2&quot;, &quot;Item 3&quot;]"',
        'defaultValue="[&quot;Item 1&quot;]"',
        'textAnchor="left"',
    ]
    helpers.test_control_builder(gui, page, expected_list)


def test_slider_text_anchor_builder(gui: Gui, test_client, helpers):
    gui._bind_var_val("x", "Item 1")
    with tgb.Page(frame=None) as page:
        tgb.slider(value="{x}", text_anchor=None)  # type: ignore[attr-defined]
    expected_list = [
        "<Slider",
        'updateVarName="_TpN_tpec_TpExPr_x_TPMDL_0"',
        "value={_TpN_tpec_TpExPr_x_TPMDL_0}",
        'textAnchor="none"',
    ]
    helpers.test_control_builder(gui, page, expected_list)


def test_slider_text_anchor_default_builder(gui: Gui, test_client, helpers):
    gui._bind_var_val("x", "Item 1")
    with tgb.Page(frame=None) as page:
        tgb.slider(value="{x}", items="Item 1")  # type: ignore[attr-defined]
    expected_list = [
        "<Slider",
        'updateVarName="_TpN_tpec_TpExPr_x_TPMDL_0"',
        "value={_TpN_tpec_TpExPr_x_TPMDL_0}",
        'textAnchor="bottom"',
    ]
    helpers.test_control_builder(gui, page, expected_list)
