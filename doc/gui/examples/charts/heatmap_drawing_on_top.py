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
import numpy

from taipy.gui import Gui


# Return the x and y coordinates of the spiral for the given angle
def spiral(th):
    a = 1.120529
    b = 0.306349
    r = a * numpy.exp(-b * th)
    return (r * numpy.cos(th), r * numpy.sin(th))


# Prepare Golden spiral data as a parametric curve
(x, y) = spiral(numpy.linspace(-numpy.pi / 13, 4 * numpy.pi, 1000))

# Prepare the heatmap x and y cell sizes along the axes
golden_ratio = (1 + numpy.sqrt(5)) / 2.0  # Golden ratio
grid_x = [0, 1, 1 + (1 / (golden_ratio**4)), 1 + (1 / (golden_ratio**3)), golden_ratio]
grid_y = [
    0,
    1 / (golden_ratio**3),
    1 / golden_ratio**3 + 1 / golden_ratio**4,
    1 / (golden_ratio**2),
    1,
]

# Main value is based on the Fibonacci sequence
z = [[13, 3, 3, 5], [13, 2, 1, 5], [13, 10, 11, 12], [13, 8, 8, 8]]

# Group all data sets in a single array
data = [
    {
        "z": z,
    },
    {"x": numpy.sort(grid_x), "y": numpy.sort(grid_y)},
    {
        "xSpiral": -x + x[0],
        "ySpiral": y - y[0],
    },
]

# Axis template: hide all ticks, lines and labels
axis = {
    "range": [0, 2.0],
    "showgrid": False,
    "zeroline": False,
    "showticklabels": False,
    "ticks": "",
    "title": "",
}

layout = {
    # Use the axis template for both x and y axes
    "xaxis": axis,
    "yaxis": axis,
}

options = {
    # Hide the color scale of the heatmap
    "showscale": False
}

# Chart holds two traces, with different types
types = ["heatmap", "scatter"]
# x and y values for both traces
xs = ["1/x", "2/xSpiral"]
ys = ["1/y", "2/ySpiral"]

page = """
<|{data}|chart|type={types}|z[1]=0/z|x={xs}|y={ys}|layout={layout}|options={options}|>
"""

if __name__ == "__main__":
    Gui(page).run(title="Chart - Heatmap - Drawing on top")
