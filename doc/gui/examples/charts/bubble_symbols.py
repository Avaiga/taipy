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
# You may need to install the yfinance package as well.
# -----------------------------------------------------------------------------------------
from taipy.gui import Gui

data = {
    "x": [1, 2, 3, 4, 5],
    "y": [10, 7, 4, 1, 5],
    "Sizes": [20, 30, 40, 50, 30],
    "Symbols": ["circle-open", "triangle-up", "hexagram", "star-diamond", "circle-cross"],
}

marker = {
    "color": "#77A",
    "size": "Sizes",
    "symbol": "Symbols",
}

page = """
<|{data}|chart|mode=markers|x=x|y=y|marker={marker}|>
"""

if __name__ == "__main__":
    Gui(page).run(title="Chart - Bubble - Symbols")
