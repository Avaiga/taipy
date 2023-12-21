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

from taipy.gui import Gui


def test_selector_md_1(gui: Gui, test_client, helpers):
    gui._bind_var_val("selected_val", ["l1", "l2"])
    gui._bind_var_val("selector_properties", {"lov": [("l1", "v1"), ("l2", "v2"), ("l3", "v3")], "filter": True})
    md_string = "<|{selected_val}|selector|properties=selector_properties|multiple|>"
    expected_list = [
        "<Selector",
        'defaultLov="[[&quot;l1&quot;, &quot;v1&quot;], [&quot;l2&quot;, &quot;v2&quot;], [&quot;l3&quot;, &quot;v3&quot;]]"',  # noqa: E501
        'defaultValue="[&quot;l1&quot;, &quot;l2&quot;]"',
        "filter={true}",
        "multiple={true}",
        'updateVarName="_TpLv_tpec_TpExPr_selected_val_TPMDL_0"',
        "value={_TpLv_tpec_TpExPr_selected_val_TPMDL_0}",
    ]
    helpers.test_control_md(gui, md_string, expected_list)


def test_selector_md_2(gui: Gui, test_client, helpers):
    gui._bind_var_val("selected_val", "Item 2")
    md_string = "<|{selected_val}|selector|lov=Item 1;Item 2; This is a another value|>"
    expected_list = [
        "<Selector",
        'defaultLov="[&quot;Item 1&quot;, &quot;Item 2&quot;, &quot; This is a another value&quot;]"',
        'defaultValue="[&quot;Item 2&quot;]"',
        'updateVarName="_TpLv_tpec_TpExPr_selected_val_TPMDL_0"',
        "value={_TpLv_tpec_TpExPr_selected_val_TPMDL_0}",
    ]
    helpers.test_control_md(gui, md_string, expected_list)


def test_selector_md_3(gui: Gui, test_client, helpers):
    gui._bind_var_val("elt", None)
    gui._bind_var_val(
        "scenario_list",
        [{"id": "1", "name": "scenario 1"}, {"id": "3", "name": "scenario 3"}, {"id": "2", "name": "scenario 2"}],
    )
    gui._bind_var_val("selected_obj", {"id": "1", "name": "scenario 1"})
    md_string = '<|{selected_obj}|selector|lov={scenario_list}|type=Scenario|adapter={lambda elt: (elt["id"], elt["name"])}|not propagate|>'  # noqa: E501
    expected_list = [
        "<Selector",
        'defaultLov="[[&quot;1&quot;, &quot;scenario 1&quot;], [&quot;3&quot;, &quot;scenario 3&quot;], [&quot;2&quot;, &quot;scenario 2&quot;]]"',  # noqa: E501
        'defaultValue="[&quot;1&quot;]"',
        "lov={_TpL_tpec_TpExPr_scenario_list_TPMDL_0}",
        "propagate={false}",
        'updateVars="lov=_TpL_tpec_TpExPr_scenario_list_TPMDL_0"',
        'updateVarName="_TpLv_tpec_TpExPr_selected_obj_TPMDL_0"',
        "value={_TpLv_tpec_TpExPr_selected_obj_TPMDL_0}",
    ]
    helpers.test_control_md(gui, md_string, expected_list)


def test_selector_html_1_1(gui: Gui, test_client, helpers):
    gui._bind_var_val("selected_val", ["l1", "l2"])
    gui._bind_var_val("selector_properties", {"lov": [("l1", "v1"), ("l2", "v2"), ("l3", "v3")], "filter": True})
    html_string = '<taipy:selector value="{selected_val}" properties="selector_properties" multiple="True"/>'
    expected_list = [
        "<Selector",
        'defaultLov="[[&quot;l1&quot;, &quot;v1&quot;], [&quot;l2&quot;, &quot;v2&quot;], [&quot;l3&quot;, &quot;v3&quot;]]"',  # noqa: E501
        'defaultValue="[&quot;l1&quot;, &quot;l2&quot;]"',
        "filter={true}",
        "multiple={true}",
        'updateVarName="_TpLv_tpec_TpExPr_selected_val_TPMDL_0"',
        "value={_TpLv_tpec_TpExPr_selected_val_TPMDL_0}",
    ]
    helpers.test_control_html(gui, html_string, expected_list)


def test_selector_html_1_2(gui: Gui, test_client, helpers):
    gui._bind_var_val("selected_val", ["l1", "l2"])
    gui._bind_var_val("selector_properties", {"lov": [("l1", "v1"), ("l2", "v2"), ("l3", "v3")], "filter": True})
    html_string = '<taipy:selector properties="selector_properties" multiple="True">{selected_val}</taipy:selector>'
    expected_list = [
        "<Selector",
        'defaultLov="[[&quot;l1&quot;, &quot;v1&quot;], [&quot;l2&quot;, &quot;v2&quot;], [&quot;l3&quot;, &quot;v3&quot;]]"',  # noqa: E501
        'defaultValue="[&quot;l1&quot;, &quot;l2&quot;]"',
        "filter={true}",
        "multiple={true}",
        'updateVarName="_TpLv_tpec_TpExPr_selected_val_TPMDL_0"',
        "value={_TpLv_tpec_TpExPr_selected_val_TPMDL_0}",
    ]
    helpers.test_control_html(gui, html_string, expected_list)


def test_selector_html_2_1(gui: Gui, test_client, helpers):
    gui._bind_var_val("selected_val", "Item 2")
    html_string = '<taipy:selector value="{selected_val}" lov="Item 1;Item 2; This is a another value" />'
    expected_list = [
        "<Selector",
        'defaultLov="[&quot;Item 1&quot;, &quot;Item 2&quot;, &quot; This is a another value&quot;]"',
        'defaultValue="[&quot;Item 2&quot;]"',
        'updateVarName="_TpLv_tpec_TpExPr_selected_val_TPMDL_0"',
        "value={_TpLv_tpec_TpExPr_selected_val_TPMDL_0}",
    ]
    helpers.test_control_html(gui, html_string, expected_list)


def test_selector_html_2_2(gui: Gui, test_client, helpers):
    gui._bind_var_val("selected_val", "Item 2")
    html_string = '<taipy:selector lov="Item 1;Item 2; This is a another value">{selected_val}</taipy:selector>'
    expected_list = [
        "<Selector",
        'defaultLov="[&quot;Item 1&quot;, &quot;Item 2&quot;, &quot; This is a another value&quot;]"',
        'defaultValue="[&quot;Item 2&quot;]"',
        'updateVarName="_TpLv_tpec_TpExPr_selected_val_TPMDL_0"',
        "value={_TpLv_tpec_TpExPr_selected_val_TPMDL_0}",
    ]
    helpers.test_control_html(gui, html_string, expected_list)
