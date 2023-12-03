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

# Flight start and end locations
data = {
    # Hartsfield-Jackson Atlanta International Airport
    # to
    # Aéroport de Paris-Charles de Gaulle
    "lat": [33.64, 49.01],
    "lon": [-84.44, 2.55],
}

layout = {
    # Chart title
    "title": "ATL to CDG",
    # Hide legend
    "showlegend": False,
    # Focus on relevant area
    "geo": {
        "resolution": 50,
        "showland": True,
        "showocean": True,
        "landcolor": "4a4",
        "oceancolor": "77d",
        "lataxis": {"range": [20, 60]},
        "lonaxis": {"range": [-100, 20]},
    },
}

# Flight displayed as a thick, red plot
line = {"width": 5, "color": "red"}

page = """
# Maps - Simple

<|{data}|chart|type=scattergeo|mode=lines|lat=lat|lon=lon|line={line}|layout={layout}|>
"""

Gui(page).run()
