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
from taipy.gui import Gui


def test_progress_builder(gui: Gui, helpers):
    with tgb.Page(frame=None) as page:
        tgb.progress(linear="true", show_value="true", value={50})  # type: ignore[attr-defined]
    expected_list = ["<Progress", 'linear={true}', 'show_value={true}', 'value="50"']
    helpers.test_control_builder(gui, page, expected_list)
