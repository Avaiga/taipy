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
# -----------------------------------------------------------------------------------------
# To execute this script, make sure that the taipy-gui package is installed in your
# Python environment and run:
#     python <script>
# -----------------------------------------------------------------------------------------
from taipy.gui import Gui

options = [("a", "Option A"), ("b", "Option B"), ("c", "Option C"), ("d", "Option D")]
selected = ["a", "b"]

def menu_action(_1, _2, payload):
    selected_options = payload["args"]
    for option in selected_options:
        print(f"Selected: {option}") # noqa: F401, T201

page = """
<|menu|lov={options}|selected={selected}|on_action=menu_action|>
"""

if __name__ == "__main__":
    Gui(page).run(title="Menu - On Action")
