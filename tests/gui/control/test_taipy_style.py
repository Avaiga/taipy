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

from taipy.gui import Gui


def test_style_in_builder(gui: Gui, helpers):
    style = {"td": { "color": "blue"  }}  # noqa: F841
    gui._set_frame(inspect.currentframe())
    md_string = "<|label|button|style={style}|>"
    expected_list = [
        "<TaipyStyle",
        'className="tpcss-',
        'content="{&quot;td&quot;: &#x7B;&quot;color&quot;: &quot;blue',
    ]
    helpers.test_control_md(gui, md_string, expected_list)

