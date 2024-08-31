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

if __name__ == "__main__":
    data = {
        "Types": ["Website visit", "Downloads", "Prospects", "Invoice sent", "Closed"],
        "Visits": [13873, 10533, 5443, 2703, 908],
    }

    marker = {
        # Boxes are filled with a blue gradient color
        "color": ["hsl(210,50%,50%)", "hsl(210,60%,60%)", "hsl(210,70%,70%)", "hsl(210,80%,80%)", "hsl(210,90%,90%)"],
        # Lines get thicker, with an orange-to-green gradient color
        "line": {"width": [1, 1, 2, 3, 4], "color": ["f5720a", "f39c1d", "f0cc3d", "aadb12", "8cb709"]},
    }

    options = {
        # Lines connecting boxes are thick, dotted and green
        "connector": {"line": {"color": "green", "dash": "dot", "width": 4}}
    }

    page = """
# Funnel Chart - Custom markers

<|{data}|chart|type=funnel|x=Visits|y=Types|marker={marker}|options={options}|>
    """

    Gui(page).run()
