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


def test_pane_md(gui: Gui, test_client, helpers):
    gui._bind_var_val("show_pane", False)
    md_string = """
<|{show_pane}|pane|not persistent|
# This is a Pane
|>
"""
    expected_list = [
        "<Pane",
        'anchor="left"',
        'updateVarName="_TpB_tpec_TpExPr_show_pane_TPMDL_0"',
        "open={_TpB_tpec_TpExPr_show_pane_TPMDL_0}",
        "<h1",
        "This is a Pane</h1></Pane>",
    ]
    helpers.test_control_md(gui, md_string, expected_list)


def test_pane_persistent_md(gui: Gui, test_client, helpers):
    gui._bind_var_val("show_pane", False)
    md_string = """
<|{show_pane}|pane|persistent|
# This is a Pane
|>
"""
    expected_list = [
        "<Pane",
        'anchor="left"',
        "persistent={true}",
        'updateVarName="_TpB_tpec_TpExPr_show_pane_TPMDL_0"',
        "open={_TpB_tpec_TpExPr_show_pane_TPMDL_0}",
        "<h1",
        "This is a Pane</h1></Pane>",
    ]
    helpers.test_control_md(gui, md_string, expected_list)


def test_pane_html(gui: Gui, test_client, helpers):
    gui._bind_var_val("show_pane", False)
    html_string = '<taipy:pane open="{show_pane}" persistent="false"><h1>This is a Pane</h1></taipy:pane>'
    expected_list = [
        "<Pane",
        'anchor="left"',
        'updateVarName="_TpB_tpec_TpExPr_show_pane_TPMDL_0"',
        "open={_TpB_tpec_TpExPr_show_pane_TPMDL_0}",
        "<h1",
        "This is a Pane</h1></Pane>",
    ]
    helpers.test_control_html(gui, html_string, expected_list)
