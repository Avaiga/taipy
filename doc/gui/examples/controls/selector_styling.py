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
import builtins

from taipy.gui import Gui, Markdown

_python_builtins = dir(builtins)
value = _python_builtins[0]

page = Markdown(
    """
<|{value}|selector|lov={_python_builtins}|>
""",
    style={
        ".taipy-selector": {
            "margin": "0px !important",  # global margin
            ".MuiInputBase-root": {  # input field
                "background-color": "#572c5f38",
                "color": "#221025",
                "border-radius": "0px",
                "height": "50px",
            },
            ".MuiList-root": {  # list
                "height": "70vh",  # limit height
                "overflow-y": "auto",  # show vertical scroll if necessary
                ".MuiListItemButton-root:nth-child(even)": {  # change colors
                    "background-color": "lightgrey",
                    "color": "darkgrey",
                },
                ".MuiListItemButton-root:nth-child(odd)": {
                    "background-color": "darkgrey",
                    "color": "lightgrey",
                },
            },
        }
    },
)

if __name__ == "__main__":
    Gui(page).run(title="Selector - Style every other row")
