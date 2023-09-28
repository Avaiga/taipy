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
from taipy.gui import Gui

# Source https://www.fao.org/faostat/en/#data/SDGB
data = {
    "Country": [
        "Rest of the world",
        "Russian Federation",
        "Brazil",
        "Canada",
        "United States of America",
        "China",
        "Australia",
        "Democratic Republic of the Congo",
        "Indonesia",
        "Peru",
    ],
    "Area": [1445674.66, 815312, 496620, 346928, 309795, 219978, 134005, 126155, 92133.2, 72330.4],
}

page = """
# Pie - Simple

<|{data}|chart|type=pie|values=Area|label=Country|>
"""

Gui(page).run()
