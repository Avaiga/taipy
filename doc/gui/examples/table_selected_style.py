# Copyright 2021-2025 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
# -----------------------------------------------------------------------------------------
# To execute this script, make sure that the taipy-gui package is installed in your
# Python environment and run:
#     python <script>
# -----------------------------------------------------------------------------------------

import taipy.gui.builder as tgb
from taipy import Gui

data = {"a": [1, 2, 3, 4, 8], "b": [5, 4, 3, 2, 1]}

selected = [0]


def select_row(state, var_name, payload):
    index = payload.get("index")
    if index in state.selected:
        state.selected = list(set(state.selected) - {index})
    else:
        state.selected = state.selected + [index]


with tgb.Page() as page:
    tgb.toggle(theme=True)

    tgb.table("{data}", selected="{selected}", on_action=select_row)

    tgb.table("{data}", selected="{selected}", on_action=select_row, class_name="rows-similar rows-bordered")


if __name__ == "__main__":
    gui = Gui(page=page)
    gui.run(run_browser=False, use_reloader=True, title= "Tables - Row Selection")
