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
from datetime import datetime

import numpy

from taipy.gui import Gui


def generate_hand_shapes():
    # Retrieve and store the current, local time
    time_now = datetime.now()
    hours = time_now.hour
    minutes = time_now.minute
    seconds = time_now.second

    # Compute the angle that represents the hours
    hours_angle = 360 * ((hours % 12) / 12 + (minutes % 60) / 60 / 60 + (seconds % 60) / 60 / 60 / 60)
    # Short and thick hand for the hours
    hours_hand = {"r": [0, 4, 5, 4, 0], "a": [0, hours_angle - 7, hours_angle, hours_angle + 7, 0]}

    # Compute the angle that represents the minutes
    minutes_angle = 360 * ((minutes % 60) / 60 + (seconds % 60) / 60 / 60)
    # Longer and slightly thinner hand for the minutes
    minutes_hand = {"r": [0, 6, 8, 6, 0], "a": [0, minutes_angle - 4, minutes_angle, minutes_angle + 4, 0]}

    # Compute the angle that represents the seconds
    seconds_angle = 360 * (seconds % 60) / 60
    # Even longer and thinner hand for the seconds
    seconds_hand = {"r": [0, 8, 10, 8, 0], "a": [0, seconds_angle - 2, seconds_angle, seconds_angle + 2, 0]}
    # Build and return the whole data set
    return [hours_hand, minutes_hand, seconds_hand]


# Update time on every refresh
def on_navigate(state, page):
    state.data = generate_hand_shapes()
    return page


if __name__ == "__main__":
    # Initialize the data set with the current time
    data = generate_hand_shapes()

    layout = {
        "polar": {
            "angularaxis": {
                "rotation": 90,
                "direction": "clockwise",
                # One tick every 30 degrees
                "tickvals": list(numpy.arange(0.0, 360.0, 30)),
                # Text value for every tick
                "ticktext": ["XII", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI"],
            },
            "radialaxis": {"angle": 90, "visible": False, "range": [0, 12]},
        },
        "showlegend": False,
    }

    # Options to be used for all three traces
    base_opts = {"fill": "toself"}
    # Specific for hours
    hours_opts = dict(base_opts)
    hours_opts["fillcolor"] = "#FF0000"
    # Specific for minutes
    minutes_opts = dict(base_opts)
    minutes_opts["fillcolor"] = "#00FF00"
    # Specific for seconds
    seconds_opts = dict(base_opts)
    seconds_opts["fillcolor"] = "#0000FF"

    # Store all the chart control properties in a single object
    properties = {
        # Don't show data point markers
        "mode": "lines",
        # Data for the hours
        "theta[1]": "0/a",
        "r[1]": "0/r",
        # Data for the minutes
        "theta[2]": "1/a",
        "r[2]": "1/r",
        # Data for the seconds
        "theta[3]": "2/a",
        "r[3]": "2/r",
        # Options for the three traces
        "options[1]": hours_opts,
        "options[2]": minutes_opts,
        "options[3]": seconds_opts,
        "line": {"color": "black"},
        "layout": layout,
    }

    page = """
# Polar - Tick texts

<|{data}|chart|type=scatterpolar|properties={properties}|>
    """
    Gui(page).run()
