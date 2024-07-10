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

import taipy.gui.builder as tgb
from taipy.gui import Gui, notify


def test_builder_on_function(gui: Gui, test_client, helpers):
    def on_slider(state):
        notify(state, "success", f"Value: {state.value}")
    gui._bind_var_val("on_slider", on_slider)
    with tgb.Page(frame=None) as page:
        tgb.slider(value="{value}", on_change=on_slider)  # type: ignore[attr-defined] # noqa: B023
    expected_list = ['<Slider','onChange="on_slider"']
    helpers.test_control_builder(gui, page, expected_list)


def test_builder_on_lambda(gui: Gui, test_client, helpers):
    with tgb.Page(frame=None) as page:
        tgb.slider(value="{value}", on_change=lambda s: notify(s, "success", f"Lambda Value: {s.value}"))  # type: ignore[attr-defined] # noqa: B023
    expected_list = ['<Slider','onChange="__lambda_']
    helpers.test_control_builder(gui, page, expected_list)
