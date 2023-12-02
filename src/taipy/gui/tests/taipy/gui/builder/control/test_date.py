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

from datetime import datetime

import taipy.gui.builder as tgb
from taipy.gui import Gui


def test_date_builder_1(gui: Gui, test_client, helpers):
    gui._bind_var_val("date", datetime.strptime("15 Dec 2020", "%d %b %Y"))
    with tgb.Page(frame=None) as page:
        tgb.date(id="date", date="{date}")
    expected_list = [
        "<DateSelector",
        'defaultDate="2020-12-',
        'updateVarName="_TpDt_tpec_TpExPr_date_TPMDL_0"',
        "date={_TpDt_tpec_TpExPr_date_TPMDL_0}",
    ]
    helpers.test_control_builder(gui, page, expected_list)


def test_date_builder_2(gui: Gui, test_client, helpers):
    gui._bind_var_val("date", datetime.strptime("15 Dec 2020", "%d %b %Y"))
    with tgb.Page(frame=None) as page:
        tgb.date(id="date", date="{date}", with_time=True)
    expected_list = [
        "<DateSelector",
        'defaultDate="2020-12-',
        'updateVarName="_TpDt_tpec_TpExPr_date_TPMDL_0"',
        "date={_TpDt_tpec_TpExPr_date_TPMDL_0}",
        "withTime={true}",
    ]
    helpers.test_control_builder(gui, page, expected_list)
