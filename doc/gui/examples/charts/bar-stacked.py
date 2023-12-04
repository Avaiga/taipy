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
import pandas
from taipy.gui import Gui

# Source https://en.wikipedia.org/wiki/List_of_United_States_presidential_elections_by_popular_vote_margin
percentages = [
    (1852, 50.83),
    (1856, 45.29),
    (1860, 39.65),
    (1864, 55.03),
    (1868, 52.66),
    (1872, 55.58),
    (1876, 47.92),
    (1880, 48.31),
    (1884, 48.85),
    (1888, 47.80),
    (1892, 46.02),
    (1896.0, 51.02),
    (1900, 51.64),
    (1904, 56.42),
    (1908, 51.57),
    (1912, 41.84),
    (1916, 49.24),
    (1920, 60.32),
    (1924, 54.04),
    (1928, 58.21),
]

# Lost percentage = 100-Won percentage
full = [(t[0], t[1], 100 - t[1]) for t in percentages]

data = pandas.DataFrame(full, columns=["Year", "Won", "Lost"])

layout = {"barmode": "stack"}

page = """
# Bar - Stacked

<|{data}|chart|type=bar|x=Year|y[1]=Won|y[2]=Lost|layout={layout}|>
"""

Gui(page).run()
