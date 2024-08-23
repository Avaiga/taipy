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
# You may need to install the yfinance package as well.
# -----------------------------------------------------------------------------------------
from taipy.gui import Gui

if __name__ == "__main__":
    data = {
        "x": [1, 2, 3],
        "y": [1, 2, 3],
        "Colors": ["blue", "green", "red"],
        "Sizes": [20, 40, 30],
        "Opacities": [1, 0.4, 1],
    }

    marker = {"color": "Colors", "size": "Sizes", "opacity": "Opacities"}

    page = """
# Bubble - Simple

<|{data}|chart|mode=markers|x=x|y=y|marker={marker}|>
    """

    Gui(page).run()
