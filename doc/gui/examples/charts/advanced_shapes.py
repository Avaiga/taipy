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


# Function to plot: x^3/3-x
def f(x):
    return x * x * x / 3 - x


# x values: [-2.2, ..., 2.2]
x = [(x - 10) / 4.5 for x in range(0, 21)]

data = {
    "x": x,
    # y: [f(-2.2), ..., f(2.2)]
    "y": [f(x) for x in x],
}

shape_size = 0.1

layout = {
    "shapes": [
        # Shape for local maximum (x = -1)
        {
            "x0": -1 - shape_size,
            "y0": f(-1) - 2 * shape_size,
            "x1": -1 + shape_size,
            "y1": f(-1) + 2 * shape_size,
            "fillcolor": "green",
            "opacity": 0.5,
        },
        # Shape for local minimum (x = 1)
        {
            "x0": 1 - shape_size,
            "y0": f(1) - 2 * shape_size,
            "x1": 1 + shape_size,
            "y1": f(1) + 2 * shape_size,
            "fillcolor": "red",
            "opacity": 0.5,
        },
    ]
}

page = """
<|{data}|chart|layout={layout}|>
"""


if __name__ == "__main__":
    Gui(page).run(title="Chart - Advanced - Shapes")
