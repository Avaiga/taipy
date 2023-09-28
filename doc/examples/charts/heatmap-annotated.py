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

data = {
    "Temperatures": [
        [17.2, 27.4, 28.6, 21.5],
        [5.6, 15.1, 20.2, 8.1],
        [26.6, 22.8, 21.8, 24.0],
        [22.3, 15.5, 13.4, 19.6],
    ],
    "Cities": ["Hanoi", "Paris", "Rio", "Sydney"],
    "Seasons": ["Winter", "Spring", "Summer", "Autumn"],
}

layout = {
    # This array contains the information we want to display in the cells
    # These are filled later
    "annotations": [],
    # No ticks on the x axis, show labels on top the of the chart
    "xaxis": {"ticks": "", "side": "top"},
    # No ticks on the y axis
    # Add a space character for a small margin with the text
    "yaxis": {"ticks": "", "ticksuffix": " "},
}

seasons = data["Seasons"]
cities = data["Cities"]
# Iterate over all cities
for city in range(len(cities)):
    # Iterate over all seasons
    for season in range(len(seasons)):
        temperature = data["Temperatures"][city][season]
        # Create the annotation
        annotation = {
            # The name of the season
            "x": seasons[season],
            # The name of the city
            "y": cities[city],
            # The temperature, as a formatted string
            "text": f"{temperature}\N{DEGREE SIGN}C",
            # Change the text color depending on the temperature
            # so it results in a better contrast
            "font": {"color": "white" if temperature < 14 else "black"},
            # Remove the annotation arrow
            "showarrow": False,
        }
        # Add the annotation to the layout's annotations array
        layout["annotations"].append(annotation)

page = """
## Heatmap - Annotated

<|{data}|chart|type=heatmap|z=Temperatures|x=Seasons|y=Cities|layout={layout}|>
"""

Gui(page).run()
