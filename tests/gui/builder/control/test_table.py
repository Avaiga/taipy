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

import taipy.gui.builder as tgb
from taipy.gui import Gui


def test_table_builder_1(gui: Gui, helpers, csvdata):
    with tgb.Page(frame=None) as page:
        tgb.table(  # type: ignore[attr-defined]
            data="{csvdata}",
            page_size=10,
            page_size_options=[10, 30, 100],
            columns=["Day", "Entity", "Code", "Daily hospital occupancy"],
            date_format="eee dd MMM yyyy",
        )
    expected_list = [
        "<Table",
        'defaultColumns="{&quot;Entity&quot;: &#x7B;&quot;index&quot;: 1, &quot;type&quot;: &quot;object&quot;, &quot;dfid&quot;: &quot;Entity&quot;&#x7D;, &quot;Code&quot;: &#x7B;&quot;index&quot;: 2, &quot;type&quot;: &quot;object&quot;, &quot;dfid&quot;: &quot;Code&quot;&#x7D;, &quot;Daily hospital occupancy&quot;: &#x7B;&quot;index&quot;: 3, &quot;type&quot;: &quot;int&quot;, &quot;dfid&quot;: &quot;Daily hospital occupancy&quot;&#x7D;, &quot;Day_str&quot;: &#x7B;&quot;index&quot;: 0, &quot;type&quot;: &quot;datetime&quot;, &quot;dfid&quot;: &quot;Day&quot;, &quot;format&quot;: &quot;eee dd MMM yyyy&quot;&#x7D;}"',  # noqa: E501
        'height="80vh"',
        'width="100%"',
        'pageSizeOptions="[10, 30, 100]"',
        "pageSize={10.0}",
        "selected={[]}",
        'updateVarName="_TpD_tpec_TpExPr_csvdata_TPMDL_0"',
        "data={_TpD_tpec_TpExPr_csvdata_TPMDL_0}",
    ]
    gui._set_frame(inspect.currentframe())
    helpers.test_control_builder(gui, page, expected_list)


def test_table_reset_builder(gui: Gui, helpers, csvdata):
    with tgb.Page(frame=None) as page:
        tgb.table(  # type: ignore[attr-defined]
            data="{csvdata}",
            rebuild=True,
            page_size=10,
            page_size_options="10;30;100",
            columns="Day;Entity;Code;Daily hospital occupancy",
            date_format="eee dd MMM yyyy",
        )
    expected_list = [
        "<Table",
        'defaultColumns="{&quot;Entity&quot;: &#x7B;&quot;index&quot;: 1, &quot;type&quot;: &quot;object&quot;, &quot;dfid&quot;: &quot;Entity&quot;&#x7D;, &quot;Code&quot;: &#x7B;&quot;index&quot;: 2, &quot;type&quot;: &quot;object&quot;, &quot;dfid&quot;: &quot;Code&quot;&#x7D;, &quot;Daily hospital occupancy&quot;: &#x7B;&quot;index&quot;: 3, &quot;type&quot;: &quot;int&quot;, &quot;dfid&quot;: &quot;Daily hospital occupancy&quot;&#x7D;, &quot;Day_str&quot;: &#x7B;&quot;index&quot;: 0, &quot;type&quot;: &quot;datetime&quot;, &quot;dfid&quot;: &quot;Day&quot;, &quot;format&quot;: &quot;eee dd MMM yyyy&quot;&#x7D;}"',  # noqa: E501
        'height="80vh"',
        'width="100%"',
        'pageSizeOptions="[10, 30, 100]"',
        "pageSize={10.0}",
        "selected={[]}",
        'updateVarName="_TpD_tpec_TpExPr_csvdata_TPMDL_0"',
        "data={_TpD_tpec_TpExPr_csvdata_TPMDL_0}",
        "columns={tp_TpExPr_gui_tbl_cols_True_None_7B_22columns_22_3A_20_22Day_3BEntity_3BCode_3BDaily_20hospital_20occupancy_22_2C_20_22date_format_22_3A_20_22eee_20dd_20MMM_20yyyy_22_7D_7B_22data_22_3A_20_22tpec_TpExPr_csvdata_TPMDL_0_22_7D_tpec_TpExPr_csvdata_TPMDL_0_csvdata_TPMDL_0_0}",
    ]
    gui._set_frame(inspect.currentframe())
    helpers.test_control_builder(gui, page, expected_list)


def test_table_builder_2(gui: Gui, helpers, csvdata):
    table_properties = {  # noqa: F841
        "page_size": 10,
        "page_size_options": [10, 50, 100, 500],
        "allow_all_rows": True,
        "columns": {
            "Day": {"index": 0, "format": "dd/MM/yyyy", "title": "Date of measure"},
            "Entity": {"index": 1},
            "Code": {"index": 2},
            "Daily hospital occupancy": {"index": 3},
        },
        "date_format": "eee dd MMM yyyy",
        "number_format": "%.3f",
        "width": "60vw",
        "height": "60vh",
    }
    with tgb.Page(frame=None) as page:
        tgb.table(data="{csvdata}", properties="table_properties", auto_loading=True, editable=True)  # type: ignore[attr-defined]
    expected_list = [
        "<Table",
        "allowAllRows={true}",
        "autoLoading={true}",
        "editable={true}",
        'onEdit="__gui.table_on_edit',
        'onDelete="__gui.table_on_delete',
        'onAdd="__gui.table_on_add',
        'defaultColumns="{&quot;Entity&quot;: &#x7B;&quot;index&quot;: 1, &quot;type&quot;: &quot;object&quot;, &quot;dfid&quot;: &quot;Entity&quot;&#x7D;, &quot;Code&quot;: &#x7B;&quot;index&quot;: 2, &quot;type&quot;: &quot;object&quot;, &quot;dfid&quot;: &quot;Code&quot;&#x7D;, &quot;Daily hospital occupancy&quot;: &#x7B;&quot;index&quot;: 3, &quot;type&quot;: &quot;int&quot;, &quot;dfid&quot;: &quot;Daily hospital occupancy&quot;, &quot;format&quot;: &quot;%.3f&quot;&#x7D;, &quot;Day_str&quot;: &#x7B;&quot;index&quot;: 0, &quot;format&quot;: &quot;dd/MM/yyyy&quot;, &quot;title&quot;: &quot;Date of measure&quot;, &quot;type&quot;: &quot;datetime&quot;, &quot;dfid&quot;: &quot;Day&quot;&#x7D;}"',  # noqa: E501
        'height="60vh"',
        'width="60vw"',
        'pageSizeOptions="[10, 50, 100, 500]"',
        "pageSize={10}",
        "selected={[]}",
        'updateVarName="_TpD_tpec_TpExPr_csvdata_TPMDL_0"',
        "data={_TpD_tpec_TpExPr_csvdata_TPMDL_0}",
    ]
    gui._set_frame(inspect.currentframe())
    helpers.test_control_builder(gui, page, expected_list)
