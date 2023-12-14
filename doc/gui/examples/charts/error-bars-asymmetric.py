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
import random

from taipy.gui import Gui

# Number of samples
n_samples = 10
# y values: [0..n_samples-1]
y = range(0, n_samples)

data = {"x": [random.uniform(1, 10) for _ in y], "y": y}

options = {
    "error_x": {
        "type": "data",
        "symmetric": False,
        "array": [random.uniform(0, 5) for _ in y],
        "arrayminus": [random.uniform(0, 2) for _ in y],
        "color": "red",
    }
}

page = """
# Error bars - Asymmetric

<|{data}|chart|type=bar|x=x|y=y|orientation=h|options={options}|>
"""

Gui(page).run()
