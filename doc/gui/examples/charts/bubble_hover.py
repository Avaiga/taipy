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

data = {
    "x": [1, 2, 3],
    "y": [1, 2, 3],
    "Texts": ["Blue<br>Small", "Green<br>Medium", "Red<br>Large"],
    "Sizes": [60, 80, 100],
    "Colors": [
        "rgb(93, 164, 214)",
        "rgb(44, 160, 101)",
        "rgb(255, 65, 54)",
    ],
}

marker = {"size": "Sizes", "color": "Colors"}

page = """
<|{data}|chart|mode=markers|x=x|y=y|marker={marker}|text=Texts|>
"""

if __name__ == "__main__":
    Gui(page).run(title="Chart - Bubble - Hover text")
