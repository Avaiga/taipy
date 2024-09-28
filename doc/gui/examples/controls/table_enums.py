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

all_continents = ["Africa", "America", "Antarctica", "Asia", "Europe", "Oceania"]
cities = [
    ("Tokyo", "Japan", "Asia", 37),
    ("Delhi", "India", "Asia", 31),
    ("Shanghai", "China", "Asia", 26),
    ("São Paulo", "Brazil", "America", 22),
    ("Cairo", "Egypt", "Africa", 20),
    ("Mexico City", "Mexico", "America", 21),
    ("New York City", "United States", "America", 8.4),
    ("Lagos", "Nigeria", "Africa", 14),
    ("Los Angeles", "United States", "America", 4),
    ("Paris", "France", "Europe", 2.2),
    ("London", "United Kingdom", "Europe", 9),
    ("Moscow", "Russia", "Europe", 12.5),
    ("Seoul", "South Korea", "Asia", 9.7),
    ("Lima", "Peru", "America", 9.5),
    ("Bogotá", "Colombia", "America", 10.9),
    ("Sydney", "Australia", "Oceania", 5.3),
]

data = {
    "City": [c[0] for c in cities],
    "Country": [c[1] for c in cities],
    "Continent": [c[2] for c in cities],
    "Population": [c[3] for c in cities],
}


page = "<|{data}|table|lov[Continent]={all_continents}|editable|no on_add|no on_delete|show_all|>"

if __name__ == "__main__":
    Gui(page).run()
