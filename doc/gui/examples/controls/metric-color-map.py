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

# color_map definition:
# - A dictionary mapping metric values to display colors.
# - Keys: Starting point of each range (number)
# - Values: Corresponding color for that range (None implies no color assignment)
# Example:
# - 20.5 maps to "#fd2020"
# - 40 maps to None (default color)
# - 60 maps to "#f3ff26"
# - 80 maps to None

value = 50
color_map = {
    20.5: "#fd2020",
    40: None,
    60: "#f3ff26",
    80: None
}

page = """
<|{value}|metric|color_map={color_map}|>
"""

Gui(page).run()

