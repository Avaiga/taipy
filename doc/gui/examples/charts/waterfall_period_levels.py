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

# Data set
data = [
    {
        # The quarterly periods are grouped by year
        "Period": [["Carry", "Q1", "Q2", "Q3", "Q4", "Current"], ["N-1", "N", "N", "N", "N", "N+1"]]
    },
    {
        "Cash Flow": [25, -17, 12, 18, -8, None],
        "Measure": ["absolute", "relative", "relative", "relative", "relative", "total"],
    },
]

page = """
<|{data}|chart|type=waterfall|x=0/Period|y=1/Cash Flow|measure=1/Measure|>
"""

if __name__ == "__main__":
    Gui(page).run(title="Chart - Waterfall - Period levels")
