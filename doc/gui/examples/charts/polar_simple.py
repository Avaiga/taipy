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
import math

from taipy.gui import Gui


# Parametric equation that draws a shape (source Wolfram Mathworld)
def draw_heart(angle):
    a = math.radians(angle)
    sa = math.sin(a)
    return 2 - 2 * sa + sa * (math.sqrt(math.fabs(math.cos(a))) / (sa + 1.4))


# One data point for each degree
theta = range(0, 360)

data = {
    # Create the heart shape
    "r": [draw_heart(angle) for angle in theta],
    "theta": theta,
}

page = """
<|{data}|chart|type=scatterpolar|mode=lines|>
"""

if __name__ == "__main__":
    Gui(page).run(title="Chart - Polar - Simple")
