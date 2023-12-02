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


def test_indicator_md(gui: Gui, test_client, helpers):
    gui._bind_var_val("val", 15)
    md_string = "<|12|indicator|value={val}|min=1|max=20|format=%.2f|>"
    expected_list = [
        "<Indicator",
        'libClassName="taipy-indicator"',
        "defaultValue={15}",
        "display={12.0}",
        'format="%.2f"',
        "max={20.0}",
        "min={1.0}",
        "value={_TpN_tpec_TpExPr_val_TPMDL_0}",
    ]
    helpers.test_control_md(gui, md_string, expected_list)


def test_menu_html(gui: Gui, test_client, helpers):
    gui._bind_var_val("val", 15)
    html_string = '<taipy:indicator value="{val}" min="1" max="20" format="%.2f" >12</taipy:indicator>'
    expected_list = [
        "<Indicator",
        'libClassName="taipy-indicator"',
        "defaultValue={15}",
        "display={12.0}",
        'format="%.2f"',
        "max={20.0}",
        "min={1.0}",
        "value={_TpN_tpec_TpExPr_val_TPMDL_0}",
    ]
    helpers.test_control_html(gui, html_string, expected_list)
