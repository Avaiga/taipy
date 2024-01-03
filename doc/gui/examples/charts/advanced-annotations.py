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


# Function to plot: x^3/3 - x
def f(x):
    return x * x * x / 3 - x


# x values: [-2.2, ..., 2.2]
x = [(x - 10) / 4.5 for x in range(0, 21)]

data = {
    "x": x,
    # y: [f(-2.2), ..., f(2.2)]
    "y": [f(x) for x in x],
}


layout = {
    # Chart title
    "title": "Local extrema",
    "annotations": [
        # Annotation for local maximum (x = -1)
        {"text": "Local <b>max</b>", "font": {"size": 20}, "x": -1, "y": f(-1)},
        # Annotation for local minimum (x = 1)
        {"text": "Local <b>min</b>", "font": {"size": 20}, "x": 1, "y": f(1), "xanchor": "left"},
    ],
}

page = """
# Advanced - Annotations

<|{data}|chart|layout={layout}|>
"""

Gui(page).run()
