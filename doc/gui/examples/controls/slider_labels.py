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

# Dictionary for slider labels
labels_with_dict = {
    0: "$0",
    1: "$1",
    2: "$2",
    3: "$3",
    4: "$4",
    5: "$5",
}

# Initial values of the sliders
value_dict = 0
value_lov=0

page = """
Labels with Dictionary

<|{value_dict}|slider|min=0|max=5|labels={labels_with_dict}|>

Value (dict): <|{value_dict}|>

Labels with List of Values (lov)

<|{value_lov}|slider|lov=0;1;2;3;4;5|labels=True|>

Value (lov): <|{value_lov}|>
"""

if __name__ == "__main__":
    Gui(page).run(title="Slider - Simple")

