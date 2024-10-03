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

# Data set: the first 10 elements of the Fibonacci sequence
n_numbers = 10
fibonacci = [0, 1]
for i in range(2, n_numbers):
    fibonacci.append(fibonacci[i - 1] + fibonacci[i - 2])

data = {"index": list(range(1, n_numbers + 1)), "fibonacci": fibonacci}

page = """
<|{data}|chart|type=treemap|labels=index|values=fibonacci|>
"""

if __name__ == "__main__":
    Gui(page).run(title="Chart - TreeMap - Simple")
