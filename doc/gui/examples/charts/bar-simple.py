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
    (1932, 57.41),
    (1936, 60.80),
    (1940, 54.74),
    (1944, 53.39),
    (1948, 49.55),
    (1952, 55.18),
    (1956, 57.37),
    (1960, 49.72),
    (1964, 61.05),
    (1968, 43.42),
    (1972, 60.67),
    (1976, 50.08),
    (1980, 50.75),
    (1984, 58.77),
    (1988, 53.37),
    (1992, 43.01),
    (1996, 49.23),
    (2000, 47.87),
    (2004, 50.73),
    (2008, 52.93),
    (2012, 51.06),
    (2016, 46.09),
    (2020, 51.31),
]
data = pandas.DataFrame(percentages, columns=["Year", "%"])

page = """
# Bar - Simple

<|{data}|chart|type=bar|x=Year|y=%|>
"""

Gui(page).run()
