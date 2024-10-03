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
# Demonstrates the use of the 'rebuild' property of the 'chart' control
# -----------------------------------------------------------------------------------------
from taipy.gui import Gui

# x values: [-10..10]
x_range = range(-10, 11)
data = {"X": x_range, "Y": [x * x for x in x_range]}

types = [("bar", "Bar"), ("line", "Line")]
selected_type = types[0]

page = """
<|{data}|chart|type={selected_type[0]}|x=X|y=Y|rebuild|>

<|{selected_type}|toggle|lov={types}|>
"""

if __name__ == "__main__":
    Gui(page).run(title="Chart - Rebuild")
