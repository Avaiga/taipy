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


def test_style_in_builder(gui: Gui, helpers):
    gui._set_frame(inspect.currentframe())
    with tgb.Page(frame=None) as page:
        tgb.button("label", style={"td": { "color": "blue"  }})  # type: ignore[attr-defined]
    expected_list = [
        "<TaipyStyle",
        'className="tpcss-',
        'content="{&quot;td&quot;: &#x7B;&quot;color&quot;: &quot;blue',
    ]
    helpers.test_control_builder(gui, page, expected_list)

