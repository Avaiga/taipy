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
    "Products": [
        "Nail polish",
        "Eyebrow pencil",
        "Rouge",
        "Lipstick",
        "Eyeshadows",
        "Eyeliner",
        "Foundation",
        "Lip gloss",
        "Mascara",
    ],
    "USA": [12814, 13012, 11624, 8814, 12998, 12321, 10342, 22998, 11261],
    "China": [3054, 5067, 7004, 9054, 12043, 15067, 10119, 12043, 10419],
    "EU": [4376, 3987, 3574, 4376, 4572, 3417, 5231, 4572, 6134],
    "Africa": [4229, 3932, 5221, 9256, 3308, 5432, 13701, 4008, 18712],
}

# Order the different traces
ys = ["USA", "China", "EU", "Africa"]

options = [
    # For the USA
    {"stackgroup": "one", "groupnorm": "percent"},
    # For China
    {"stackgroup": "one"},
    # For the EU
    {"stackgroup": "one"},
    # For Africa
    {"stackgroup": "one"},
]

layout = {
    # Show all values when hovering on a data point
    "hovermode": "x unified"
}

page = """
<|{data}|chart|mode=none|x=Products|y={ys}|options={options}|layout={layout}|>
"""

if __name__ == "__main__":
    Gui(page).run(title="Chart - Filled Area - Stacked Normalized")
