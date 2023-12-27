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
import random

from taipy.gui import Gui

# Random set of 100 samples
samples = {"x": [random.gauss(mu=0.0, sigma=1.0) for _ in range(100)]}

# Use the same data for both traces
data = [samples, samples]

options = [
    # First data set displayed as green-ish, and 5 bins
    {"marker": {"color": "#4A4"}, "nbinsx": 5},
    # Second data set displayed as red-ish, and 25 bins
    {"marker": {"color": "#A33"}, "nbinsx": 25},
]

layout = {
    # Overlay the two histograms
    "barmode": "overlay",
    # Hide the legend
    "showlegend": False,
}

page = """
# Histogram - NBins

<|{data}|chart|type=histogram|options={options}|layout={layout}|>
"""
Gui(page).run()
