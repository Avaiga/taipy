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
        "Month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
        "Milk": [80, 85, 95, 120, 140, 130, 145, 150, 120, 100, 90, 110],
        "Bread": [100, 90, 85, 90, 100, 110, 105, 95, 100, 110, 120, 125],
        "Apples": [50, 65, 70, 65, 70, 75, 85, 70, 60, 65, 70, 80],
    }

    # Name of the three sets to trace
    items = ["Milk", "Bread", "Apples"]

    options = {
        # Group all traces in the same stack group
        "stackgroup": "first_group"
    }

    page = """
# Filled Area - Stacked

<|{data}|chart|mode=none|x=Month|y={items}|options={options}|>
    """

    Gui(page).run()
