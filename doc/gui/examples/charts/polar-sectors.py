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

# Sample small plot definition
trace = {
    "r": [1, 2, 3, 4, 1],
    "theta": [0, 40, 80, 120, 160],
}

# The same data is used in both traces
data = [trace, trace]

# Naming the subplot is mandatory to get them both in
# the same chart
options = [
    {
        "subplot": "polar",
    },
    {"subplot": "polar2"},
]

layout = {
    # Hide the legend
    "showlegend": False,
    # Restrict the angular values for second trace
    "polar2": {"sector": [30, 130]},
}

md = """
# Polar - Sectors

<|{data}|chart|type=scatterpolar|layout={layout}|options={options}|>
"""

Gui(md).run()
