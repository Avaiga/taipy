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
import random
from typing import List

import numpy

from taipy.gui import Gui


def on_change(state, var, val):
    if var == "selected_indices":
        state.mean_value = numpy.mean([data["y"][idx] for idx in val]) if len(val) else 0


if __name__ == "__main__":
    # x = [0..20]
    x = list(range(0, 21))

    data = {
        "x": x,
        # A list of random values within [1, 10]
        "y": [random.uniform(1, 10) for _ in x],
    }

    layout = {
        # Force the Box select tool
        "dragmode": "select",
        # Remove all margins around the plot
        "margin": {"l": 0, "r": 0, "b": 0, "t": 0},
    }

    config = {
        # Hide Plotly's mode bar
        "displayModeBar": False
    }

    selected_indices: List = []

    mean_value = 0.0

    page = """
## Mean of <|{len(selected_indices)}|raw|> selected points: <|{mean_value}|format=%.2f|raw|>

<|{data}|chart|selected={selected_indices}|layout={layout}|plot_config={config}|>
    """

    Gui(page).run(title="Chart - Advanced - Selection")
