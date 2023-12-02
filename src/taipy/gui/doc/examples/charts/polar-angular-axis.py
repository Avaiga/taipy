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
# -----------------------------------------------------------------------------------------
# To execute this script, make sure that the taipy-gui package is installed in your
# Python environment and run:
#     python <script>
# -----------------------------------------------------------------------------------------
from taipy.gui import Gui

# Create a star shape
data = {"r": [3, 1] * 5 + [3], "theta": list(range(0, 360, 36)) + [0]}

options = [
    # First plot is filled with a yellow-ish color
    {"subplot": "polar", "fill": "toself", "fillcolor": "#E4FF87"},
    # Second plot is filled with a blue-ish color
    {"fill": "toself", "subplot": "polar2", "fillcolor": "#709BFF"},
]

layout = {
    "polar": {
        # This actually is the default value
        "angularaxis": {
            "direction": "counterclockwise",
        },
    },
    "polar2": {
        "angularaxis": {
            # Rotate the axis 180° (0 is on the left)
            "rotation": 180,
            # Orient the axis clockwise
            "direction": "clockwise",
            # Show the angles as radians
            "thetaunit": "radians",
        },
    },
    # Hide the legend
    "showlegend": False,
}

page = """
# Polar Charts - Direction

<|{data}|chart|type=scatterpolar|layout={layout}|options={options}|>
"""

Gui(page).run()
