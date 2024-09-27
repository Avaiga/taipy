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

from taipy.gui import Gui

# Common axis for all data: [1..10]
x = list(range(1, 11))
# Sample data
samples = [5, 7, 8, 4, 5, 9, 8, 8, 6, 5]

# Generate error data
# Error that adds to the input data
error_plus = [3 * random.random() + 0.5 for _ in x]
# Error subtracted from to the input data
error_minus = [3 * random.random() + 0.5 for _ in x]

# Upper bound (y + error_plus)
error_upper = [y + e for (y, e) in zip(samples, error_plus)]
# Lower bound (y - error_minus)
error_lower = [y - e for (y, e) in zip(samples, error_minus)]

data = [
    # Trace for samples
    {"x": x, "y": samples},
    # Trace for error range
    {
        # Roundtrip around the error bounds: onward then return
        "x": x + list(reversed(x)),
        # The two error bounds, with lower bound reversed
        "y": error_upper + list(reversed(error_lower)),
    },
]

properties = {
    # Error data
    "x[1]": "1/x",
    "y[1]": "1/y",
    "options[1]": {
        # Shows as filled area
        "fill": "toself",
        "fillcolor": "rgba(70,70,240,0.6)",
        "showlegend": False,
    },
    # Don't show surrounding stroke
    "color[1]": "transparent",
    # Raw data (displayed on top of the error band)
    "x[2]": "0/x",
    "y[2]": "0/y",
    "color[2]": "rgb(140,50,50)",
    # Shown in the legend
    "name[2]": "Input",
}

page = """
<|{data}|chart|properties={properties}|>
"""

if __name__ == "__main__":
    Gui(page).run(title="Chart - Continuous Error - Simple")
