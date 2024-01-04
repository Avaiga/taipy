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

# x values are [-10..10]
x_range = range(-10, 11)

# The data set holds the _x_ series and two distinct series for _y_
data = {
    "x": x_range,
    # y1 = x*x
    "y1": [x * x for x in x_range],
    # y2 = 100-x*x
    "y2": [100 - x * x for x in x_range],
}

page = """
# Basics - Multiple traces

<|{data}|chart|x=x|y[1]=y1|y[2]=y2|>
"""

Gui(page).run()
