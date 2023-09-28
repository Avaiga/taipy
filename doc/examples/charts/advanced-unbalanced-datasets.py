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

# The first data set uses the x interval [-10..10],
# with one point at every other unit
x1_range = [x * 2 for x in range(-5, 6)]

# The second data set uses the x interval [-4..4],
# with ten point between every unit
x2_range = [x / 10 for x in range(-40, 41)]

# Definition of the two data sets
data = [
    # Coarse data set
    {"x": x1_range, "Coarse": [x * x for x in x1_range]},
    # Fine data set
    {"x": x2_range, "Fine": [x * x for x in x2_range]},
]

page = """
# Advanced - Unbalanced data sets

<|{data}|chart|x[1]=0/x|y[1]=0/Coarse|x[2]=1/x|y[2]=1/Fine|>
"""

Gui(page).run()
