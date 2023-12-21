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
import datetime

import dateutil.relativedelta

from taipy.gui import Gui

# Data is collected from January 1st, 2010, every month
start_date = datetime.datetime(year=2010, month=1, day=1)
period = dateutil.relativedelta.relativedelta(months=1)

# Data
# All arrays have the same size (the number of months to track)
prices = {
    # Data for apples
    "apples": [2.48, 2.47, 2.5, 2.47, 2.46, 2.38, 2.31, 2.25, 2.39, 2.41, 2.59, 2.61],
    "apples_low": [1.58, 1.58, 1.59, 1.64, 1.79, 1.54, 1.53, 1.61, 1.65, 2.02, 1.92, 1.54],
    "apples_high": [3.38, 3.32, 2.63, 2.82, 2.58, 2.53, 3.27, 3.15, 3.44, 3.42, 3.08, 2.86],
    "bananas": [2.94, 2.50, 2.39, 2.77, 2.43, 2.32, 2.37, 1.90, 2.31, 2.71, 3.38, 1.92],
    "bananas_low": [2.12, 1.90, 1.69, 2.44, 1.58, 1.81, 1.44, 1.00, 1.59, 1.74, 2.78, 0.96],
    "bananas_high": [3.32, 2.70, 3.12, 3.25, 3.00, 2.63, 2.54, 2.37, 2.97, 3.69, 4.36, 2.95],
    "cherries": [6.18, None, None, None, 3.69, 2.46, 2.31, 2.57, None, None, 6.50, 4.38],
    "cherries_high": [7.00, None, None, None, 8.50, 6.27, 5.61, 4.36, None, None, 8.00, 7.23],
    "cherries_low": [3.55, None, None, None, 1.20, 0.87, 1.08, 1.50, None, None, 5.00, 4.20],
}

# Create monthly time series
months = [start_date + n * period for n in range(0, len(prices["apples"]))]

data = [
    # Raw data
    {"Months": months, "apples": prices["apples"], "bananas": prices["bananas"], "cherries": prices["cherries"]},
    # Range data (twice as many values)
    {
        "Months2": months + list(reversed(months)),
        "apples": prices["apples_high"] + list(reversed(prices["apples_low"])),
        "bananas": prices["bananas_high"] + list(reversed(prices["bananas_low"])),
        "cherries": prices["cherries_high"] + list(reversed(prices["cherries_low"])),
    },
]

properties = {
    # First trace: reference for Apples
    "x[1]": "0/Months",
    "y[1]": "0/apples",
    "color[1]": "rgb(0,200,80)",
    #     Hide line
    "mode[1]": "markers",
    #     Show in the legend
    "name[1]": "Apples",
    # Second trace: reference for Bananas
    "x[2]": "0/Months",
    "y[2]": "0/bananas",
    "color[2]": "rgb(0,100,240)",
    #     Hide line
    "mode[2]": "markers",
    #     Show in the legend
    "name[2]": "Bananas",
    # Third trace: reference for Cherries
    "x[3]": "0/Months",
    "y[3]": "0/cherries",
    "color[3]": "rgb(240,60,60)",
    #     Hide line
    "mode[3]": "markers",
    #     Show in the legend
    "name[3]": "Cherries",
    # Fourth trace: range for Apples
    "x[4]": "1/Months2",
    "y[4]": "1/apples",
    "options[4]": {
        "fill": "tozerox",
        "showlegend": False,
        "fillcolor": "rgba(0,100,80,0.4)",
    },
    #      No surrounding stroke
    "color[4]": "transparent",
    # Fifth trace: range for Bananas
    "x[5]": "1/Months2",
    "y[5]": "1/bananas",
    "options[5]": {"fill": "tozerox", "showlegend": False, "fillcolor": "rgba(0,180,250,0.4)"},
    #      No surrounding stroke
    "color[5]": "transparent",
    # Sixth trace: range for Cherries
    "x[6]": "1/Months2",
    "y[6]": "1/cherries",
    "options[6]": {
        "fill": "tozerox",
        "showlegend": False,
        "fillcolor": "rgba(230,100,120,0.4)",
    },
    #      No surrounding stroke
    "color[6]": "transparent",
}

page = """
# Continuous Error - Multiple traces

<|{data}|chart|properties={properties}|>
"""

Gui(page).run()
