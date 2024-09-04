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

from datetime import datetime

from taipy.gui import Gui


def test_date_md_1(gui: Gui, test_client, helpers):
    gui._bind_var_val("date", datetime.strptime("15 Dec 2020", "%d %b %Y"))
    md_string = "<|{date}|date|>"
    expected_list = [
        "<DateSelector",
        'defaultDate="2020-12-',
        'updateVarName="_TpDt_tpec_TpExPr_date_TPMDL_0"',
        "date={_TpDt_tpec_TpExPr_date_TPMDL_0}",
    ]
    helpers.test_control_md(gui, md_string, expected_list)


def test_date_md_2(gui: Gui, test_client, helpers):
    gui._bind_var_val("date", datetime.strptime("15 Dec 2020", "%d %b %Y"))
    md_string = "<|{date}|date|with_time|label=a label|>"
    expected_list = [
        "<DateSelector",
        'defaultDate="2020-12-',
        'updateVarName="_TpDt_tpec_TpExPr_date_TPMDL_0"',
        "date={_TpDt_tpec_TpExPr_date_TPMDL_0}",
        "withTime={true}",
        'label="a label"',
    ]
    helpers.test_control_md(gui, md_string, expected_list)


def test_date_md_width(gui: Gui, test_client, helpers):
    gui._bind_var_val("date", datetime.strptime("15 Dec 2020", "%d %b %Y"))
    md_string = "<|{date}|date|width=70%|>"
    expected_list = [
        "<DateSelector",
        'defaultDate="2020-12-',
        'updateVarName="_TpDt_tpec_TpExPr_date_TPMDL_0"',
        'width="70%"',
        "date={_TpDt_tpec_TpExPr_date_TPMDL_0}",
    ]
    helpers.test_control_md(gui, md_string, expected_list)


def test_date_html_1(gui: Gui, test_client, helpers):
    gui._bind_var_val("date", datetime.strptime("15 Dec 2020", "%d %b %Y"))
    html_string = '<taipy:date date="{date}" />'
    expected_list = [
        "<DateSelector",
        'defaultDate="2020-12-',
        'updateVarName="_TpDt_tpec_TpExPr_date_TPMDL_0"',
        "date={_TpDt_tpec_TpExPr_date_TPMDL_0}",
    ]
    helpers.test_control_html(gui, html_string, expected_list)


def test_date_html_2(gui: Gui, test_client, helpers):
    gui._bind_var_val("date", datetime.strptime("15 Dec 2020", "%d %b %Y"))
    html_string = "<taipy:date>{date}</taipy:date>"
    expected_list = [
        "<DateSelector",
        'defaultDate="2020-12-',
        'updateVarName="_TpDt_tpec_TpExPr_date_TPMDL_0"',
        "date={_TpDt_tpec_TpExPr_date_TPMDL_0}",
    ]
    helpers.test_control_html(gui, html_string, expected_list)
