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

data = [
    {
        "x": [1, 2, 3, 4],
        "y": [10, 11, 12, 13],
    },
    {
        "x": [1, 2, 3, 4],
        "y": [11, 12, 13, 14],
    },
    {
        "x": [1, 2, 3, 4],
        "y": [12, 13, 14, 15],
    },
]

options = [
    # First data set is represented by increasingly large
    # disks, getting more and more opaque
    {"marker": {"color": "red", "size": [12, 22, 32, 42], "opacity": [0.2, 0.5, 0.7, 1]}},
    # Second data set is represented with a different symbol
    # for each data point
    {
        "marker": {"color": "blue", "size": 18, "symbol": ["circle", "square", "diamond", "cross"]},
    },
    # Third data set is represented with green disks surrounded
    # by a red circle that becomes thicker and thicker
    {
        "marker": {"color": "green", "size": 20, "line": {"color": "red", "width": [2, 4, 6, 8]}},
    },
]

markers = [
    # First data set is represented by increasingly large
    # disks, getting more and more opaque
    {"color": "red", "size": [12, 22, 32, 42], "opacity": [0.2, 0.5, 0.7, 1]},
    # Second data set is represented with a different symbol
    # for each data point
    {"color": "blue", "size": 18, "symbol": ["circle", "square", "diamond", "cross"]},
    # Third data set is represented with green disks surrounded
    # by a red circle that becomes thicker and thicker
    {"color": "green", "size": 20, "line": {"color": "red", "width": [2, 4, 6, 8]}},
]

layout = {
    # Hide the chart legend
    "showlegend": False,
    # Remove all ticks from the x axis
    "xaxis": {"showticklabels": False},
    # Remove all ticks from the y axis
    "yaxis": {"showticklabels": False},
}

page = """
## Scatter - Customize markers

<|{data}|chart|mode=markers|layout={layout}|marker={markers}|>
"""

Gui(page).run()
