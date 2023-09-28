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
import math

# One data point for each degree
theta = range(0, 360)


# Create a rose-like shaped radius-array
def create_rose(n_petals):
    return [math.cos(math.radians(n_petals * angle)) for angle in theta]


data = {"theta": theta, "r1": create_rose(2), "r2": create_rose(3), "r3": create_rose(4)}

# We want three traces in the same chart
r = ["r1", "r2", "r3"]

layout = {
    # Hide the legend
    "showlegend": False,
    "polar": {
        # Hide the angular axis
        "angularaxis": {"visible": False},
        # Hide the radial axis
        "radialaxis": {"visible": False},
    },
}

page = """
# Polar - Multiple

<|{data}|chart|type=scatterpolar|mode=lines|r={r}|theta=theta|layout={layout}|>
"""

Gui(page).run()
