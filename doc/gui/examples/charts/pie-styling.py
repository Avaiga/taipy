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

n_slices = 20
# List: [1..n_slices]
# Slices are bigger and bigger
values = list(range(1, n_slices + 1))

marker = {
    # Colors move around the Hue color disk
    "colors": [f"hsl({360 * (i - 1)/(n_slices - 1)},90%,60%)" for i in values]
}

layout = {
    # Hide the legend
    "showlegend": False
}

options = {
    # Hide the texts
    "textinfo": "none"
}

page = """
# Pie - Style

<|{values}|chart|type=pie|marker={marker}|options={options}|layout={layout}|>
"""

Gui(page).run()
