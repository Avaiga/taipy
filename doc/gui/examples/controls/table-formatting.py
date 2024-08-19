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
import datetime

from taipy.gui import Gui

stock = {
    "date": [datetime.datetime(year=2000, month=12, day=d) for d in range(20, 30)],
    "price": [119.88, 112.657, 164.5, 105.42, 188.36, 103.9, 143.97, 160.11, 136.3, 174.06],
    "change": [7.814, -5.952, 0.01, 8.781, 7.335, 6.623, -6.635, -6.9, 0.327, -0.089],
    "volume": [773, 2622, 2751, 1108, 7400, 3772, 9398, 4444, 9264, 1108],
}

columns = {
    "date": {"title": "Data", "format": "MMM d"},
    "price": {"title": "Price", "format": "$%.02f"},
    "change": {"title": "% change", "format": "%.01f"},
    "volume": {"title": "Volume"},
}

page = """
# Formatting cells in a table

<|{stock}|table|columns={columns}|>
"""

Gui(page).run()
