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

data = {
    "John_us": [500, 450, 340, 230, 220, 110],
    "John_eu": [600, 500, 400, 300, 200, 100],
    "Robert_us": [510, 480, 440, 330, 220, 100],
    "Robert_eu": [360, 250, 240, 130, 120, 60],
}

# Values for each trace
values = ["John_us", "John_eu", "Robert_us", "Robert_eu"]

options = [
    # For John/US
    {
        "scalegroup": "first",
        "textinfo": "value",
        "title": {
            # "position": "top",
            "text": "John in the U.S."
        },
        # Lower-left corner
        "domain": {"x": [0, 0.5], "y": [0, 0.5]},
    },
    # For John/EU
    {
        "scalegroup": "first",
        "textinfo": "value",
        "title": {
            # "position": "top",
            "text": "John in the E.U."
        },
        # Upper-left corner
        "domain": {"x": [0, 0.5], "y": [0.55, 1]},
    },
    # For Robert/US
    {
        "scalegroup": "second",
        "textinfo": "value",
        "title": {
            # "position": "top",
            "text": "Robert in the U.S."
        },
        # Lower-right corner
        "domain": {"x": [0.51, 1], "y": [0, 0.5]},
    },
    # For Robert/EU
    {
        "scalegroup": "second",
        "textinfo": "value",
        "title": {
            # "position": "top",
            "text": "Robert in the E.U."
        },
        # Upper-right corner
        "domain": {"x": [0.51, 1], "y": [0.51, 1]},
    },
]

layout = {
    "title": "Sales per Salesman per Region",
    "showlegend": False,
    # Draw frames around each trace
    "shapes": [
        {"x0": 0, "x1": 0.5, "y0": 0, "y1": 0.5},
        {"x0": 0, "x1": 0.5, "y0": 0.52, "y1": 1},
        {"x0": 0.52, "x1": 1, "y0": 0, "y1": 0.5},
        {"x0": 0.52, "x1": 1, "y0": 0.52, "y1": 1},
    ],
}

page = """
# Funnel Area - Multiple Charts

<|{data}|chart|type=funnelarea|values={values}|options={options}|layout={layout}|>
"""

Gui(page).run()
