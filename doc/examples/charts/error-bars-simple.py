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
import random

# Number of samples
max_x = 20
# x values: [0..max_x-1]
x = range(0, max_x)
# Generate random sampling error margins
error_ranges = [random.uniform(0, 5) for _ in x]
# Compute a perfect sine wave
perfect_y = [10 * math.sin(4 * math.pi * i / max_x) for i in x]
# Compute a sine wave impacted by the sampling error
# The error is between ±error_ranges[x]/2
y = [perfect_y[i] + random.uniform(-error_ranges[i] / 2, error_ranges[i] / 2) for i in x]

# The chart data is made of the three series
data = {
    "x": x,
    "y1": y,
    "y2": perfect_y,
}

options = {
    # Create the error bar information:
    "error_y": {"type": "data", "array": error_ranges}
}

page = """
# Error bars - Simple

<|{data}|chart|x=x|y[1]=y1|y[2]=y2|options[1]={options}|>
"""

Gui(page).run()
