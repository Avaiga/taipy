# Copyright 2021-2025 Avaiga Private Limited
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
from taipy.gui import Gui, Markdown

value = "Item 2"

page = Markdown(
    "<|{value}|toggle|lov=Item 1;Item 2;Item 3;Item 4;Item 5|>",
    style={
        ".taipy-toggle": {
            ".MuiToggleButtonGroup-root": {  # Select the buttons group
                ".MuiToggleButton-root:nth-child(even)": {  # Style for even buttons
                    "background-color": "lightgrey",
                    "color": "black",
                },
                ".MuiToggleButton-root:nth-child(odd)": {  # Style for odd buttons
                    "background-color": "darkgrey",
                    "color": "white",
                },
            },
        }
    },
)

if __name__ == "__main__":
    Gui(page).run(title="Toggle - Styling")
