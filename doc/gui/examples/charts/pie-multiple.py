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

# List of countries, used as labels in the pie charts
countries = ["US", "China", "European Union", "Russian Federation", "Brazil", "India", "Rest of World"]

data = [
    {
        # Values for GHG Emissions
        "values": [16, 15, 12, 6, 5, 4, 42],
        "labels": countries,
    },
    {
        # Values for CO2 Emissions
        "values": [27, 11, 25, 8, 1, 3, 25],
        "labels": countries,
    },
]

options = [
    # First pie chart
    {
        # Show label value on hover
        "hoverinfo": "label",
        # Leave a hole in the middle of the chart
        "hole": 0.4,
        # Place the trace on the left side
        "domain": {"column": 0},
    },
    # Second pie chart
    {
        # Show label value on hover
        "hoverinfo": "label",
        # Leave a hole in the middle of the chart
        "hole": 0.4,
        # Place the trace on the right side
        "domain": {"column": 1},
    },
]

layout = {
    # Chart title
    "title": "Global Emissions 1990-2011",
    # Show traces in a 1x2 grid
    "grid": {"rows": 1, "columns": 2},
    "annotations": [
        # Annotation for the first trace
        {
            "text": "GHG",
            "font": {"size": 20},
            # Hide annotation arrow
            "showarrow": False,
            # Move to the center of the trace
            "x": 0.18,
            "y": 0.5,
        },
        # Annotation for the second trace
        {
            "text": "CO2",
            "font": {"size": 20},
            "showarrow": False,
            # Move to the center of the trace
            "x": 0.81,
            "y": 0.5,
        },
    ],
    "showlegend": False,
}

page = """
# Pie - Multiple

<|{data}|chart|type=pie|x[1]=0/values|x[2]=1/values|options={options}|layout={layout}|>
"""

Gui(page).run()
