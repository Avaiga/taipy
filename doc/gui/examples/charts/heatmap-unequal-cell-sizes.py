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
from itertools import accumulate

import numpy as np

from taipy.gui import Gui

if __name__ == "__main__":
    grid_size = 10
    data = [
        {
            # z is set to:
            # - 0 if row+col is a multiple of 4
            # - 1 if row+col is a multiple of 2
            # - 0.5 otherwise
            "z": [
                [0.0 if (row + col) % 4 == 0 else 1 if (row + col) % 2 == 0 else 0.5 for col in range(grid_size)]
                for row in range(grid_size)
            ]
        },
        {
            # A series of coordinates, growing exponentially
            "x": [0] + list(accumulate(np.logspace(0, 1, grid_size))),
            # A series of coordinates, shrinking exponentially
            "y": [0] + list(accumulate(np.logspace(1, 0, grid_size))),
        },
    ]

    # Axis template used in the layout object
    axis_template = {
        # Don't show any line or tick or label
        "showgrid": False,
        "zeroline": False,
        "ticks": "",
        "showticklabels": False,
        "visible": False,
    }

    layout = {"xaxis": axis_template, "yaxis": axis_template}

    options = {
        # Remove the color scale display
        "showscale": False
    }

    page = """
## Heatmap - Unequal block sizes

<|{data}|chart|type=heatmap|z=0/z|x=1/x|y=1/y|layout={layout}|options={options}|>
    """

    Gui(page).run()
