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

# 9-hole course
n_holes = 9

# Data set
# Each entry holds an array of values. One for each hole, plus one for th
data = {
    # ["Hole1", "Hole2", ..., "Hole9"]
    "Hole": [f"Hole{h}" for h in range(1, n_holes + 1)] + ["Score"],
    # Par for each hole
    "Par": [3, 4, 4, 5, 3, 5, 4, 5, 3] + [None],  # type: ignore
    # Score for each hole
    "Score": [4, 4, 5, 4, 4, 5, 4, 5, 4] + [None],  # type: ignore
    # Represented as relative values except for the last one
    "M": n_holes * ["relative"] + ["total"],
}

# Compute difference (Score-Par)
data["Diff"] = [data["Score"][i] - data["Par"][i] for i in range(0, n_holes)] + [None]  # type: ignore[index]

# Show positive values in red, and negative values in green
options = {"decreasing": {"marker": {"color": "green"}}, "increasing": {"marker": {"color": "red"}}}

page = """
<|{data}|chart|type=waterfall|x=Hole|y=Diff|measure=M|options={options}|>
"""

if __name__ == "__main__":
    Gui(page).run(title="Chart - Waterfall - Styling")
