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
    # Major countries and their surface (in km2), for every continent
    # Source: https://en.wikipedia.org/wiki/List_of_countries_and_dependencies_by_area
    continents = {
        "Africa": [
            {"name": "Algeria", "surface": 2381741},
            {"name": "Dem. Rep. Congo", "surface": 2344858},
            {"name": "Sudan", "surface": 1886068},
            {"name": "Libya", "surface": 1759540},
            {"name": "Chad", "surface": 1284000},
        ],
        "Asia": [
            {"name": "Russia-Asia", "surface": 17098246},
            {"name": "China", "surface": 9596961},
            {"name": "India", "surface": 3287263},
            {"name": "Kazakhstan", "surface": 2724900},
            {"name": "Saudi Arabia", "surface": 2149690},
        ],
        "Europe": [
            {"name": "Russia-Eur", "surface": 3972400},
            {"name": "Ukraine", "surface": 603628},
            {"name": "France", "surface": 551695},
            {"name": "Spain", "surface": 498980},
            {"name": "Sweden", "surface": 450295},
        ],
        "Americas": [
            {"name": "Canada", "surface": 9984670},
            {"name": "U.S.A.", "surface": 9833517},
            {"name": "Brazil", "surface": 8515767},
            {"name": "Argentina", "surface": 2780400},
            {"name": "Mexico", "surface": 1964375},
        ],
        "Oceania": [
            {"name": "Australia", "surface": 7692024},
            {"name": "Papua New Guinea", "surface": 462840},
            {"name": "New Zealand", "surface": 270467},
            {"name": "Solomon Islands", "surface": 28896},
            {"name": "Fiji", "surface": 18274},
        ],
        "Antarctica": [{"name": "Whole", "surface": 14200000}],
    }

    name: list = []
    surface: list = []
    continent: list = []

    for continent_name, countries in continents.items():
        # Create continent in root rectangle
        name.append(continent_name)
        surface.append(0)
        continent.append("")
        # Create countries in that continent rectangle
        for country in countries:
            name.append(country["name"])
            surface.append(country["surface"])
            continent.append(continent_name)

    data = {"names": name, "surfaces": surface, "continent": continent}

    page = """
# TreeMap - Hierarchical values

<|{data}|chart|type=treemap|labels=names|values=surfaces|parents=continent|>
    """

    Gui(page).run()
