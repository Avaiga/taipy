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
# Face-to-face bar charts example
import numpy
from taipy.gui import Gui

n_years = 10

proportions_female = numpy.zeros(n_years)
proportions_male = numpy.zeros(n_years)

# Prepare the data set with random variations
proportions_female[0] = 0.4
proportions_male[0] = proportions_female[0] * (1 + numpy.random.normal(0, 0.1))

for i in range(1, n_years):
    mean_i = (0.5 - proportions_female[i - 1]) / 5
    new_value = proportions_female[i - 1] + numpy.random.normal(mean_i, 0.1)

    new_value = min(max(0, new_value), 1)
    proportions_female[i] = new_value
    proportions_male[i] = proportions_female[i] * (1 + numpy.random.normal(0, 0.1))


data = {
    "Hobbies": [
        "Archery",
        "Tennis",
        "Football",
        "Basket",
        "Volley",
        "Golf",
        "Video-Games",
        "Reading",
        "Singing",
        "Music",
    ],
    "Female": proportions_female,
    # Negate these values so they appear to the left side
    "Male": -proportions_male,
}

properties = {
    # Shared y values
    "y": "Hobbies",
    # Bars for the female data set
    "x[1]": "Female",
    "color[1]": "#c26391",
    # Bars for the male data set
    "x[2]": "Male",
    "color[2]": "#5c91de",
    # Both data sets are represented with an horizontal orientation
    "orientation": "h",
    #
    "layout": {
        # This makes left and right bars aligned on the same y value
        "barmode": "overlay",
        # Set a relevant title for the x axis
        "xaxis": {"title": "Gender"},
        # Hide the legend
        "showlegend": False,
        "margin": {"l": 100},
    },
}

page = """
# Bar - Facing

<|{data}|chart|type=bar|properties={properties}|>
"""

Gui(page).run()
