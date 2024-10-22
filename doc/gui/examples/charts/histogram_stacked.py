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

# Data set made of two series of random numbers
data = {"A": [random.random() for _ in range(200)], "B": [random.random() for _ in range(200)]}

# Names of the two traces
names = ["A samples", "B samples"]

layout = {
    # Make the histogram stack the data sets
    "barmode": "stack"
}

page = """
<|{data}|chart|type=histogram|x[1]=A|x[2]=B|name={names}|layout={layout}|>
"""

if __name__ == "__main__":
    Gui(page).run(title="Chart - Histogram - Stacked")
