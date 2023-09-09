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

import taipy.gui.builder as tgb
from taipy.gui import Gui


def test_navbar_builder(gui: Gui, test_client, helpers):
    gui._bind_var_val(
        "navlov",
        [
            ("/page1", "Page 1"),
            ("/page2", "Page 2"),
            ("/page3", "Page 3"),
            ("/page4", "Page 4"),
        ],
    )
    with tgb.Page(frame=None) as page:
        tgb.navbar(lov="{navlov}")
    expected_list = [
        "<NavBar",
        'defaultLov="[[&quot;/page1&quot;, &quot;Page 1&quot;], [&quot;/page2&quot;, &quot;Page 2&quot;], [&quot;/page3&quot;, &quot;Page 3&quot;], [&quot;/page4&quot;, &quot;Page 4&quot;]]"',
        "lov={_TpL_tpec_TpExPr_navlov_TPMDL_0}",
    ]
    helpers.test_control_builder(gui, page, expected_list)
