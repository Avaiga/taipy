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
        "Day": ["Mon", "Tue", "Wed", "Thu", "Fri"],
        "Items": [32, 25, 86, 60, 70],
        "Price": [80, 50, 140, 10, 70],
    }

    options = [
        # For items
        {"fill": "tozeroy"},
        # For price
        # Using "tonexty" not to cover the first trace
        {"fill": "tonexty"},
    ]

    page = """
# Filled Area - Overlay

<|{data}|chart|mode=none|x=Day|y[1]=Items|y[2]=Price|options={options}|>
    """

    Gui(page).run()
