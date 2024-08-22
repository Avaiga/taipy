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
    # x values are [-10..10]
    x_range = range(-10, 11)

    # The data set holds the _x_ series and two distinct series for _y_
    data = {
        "x": x_range,
        # y1 = x*x
        "y1": [x * x for x in x_range],
        # y2 = 2-x*x/50
        "y2": [(100 - x * x) / 50 for x in x_range],
    }

    layout = {
        "yaxis2": {
            # Second axis overlays with the first y axis
            "overlaying": "y",
            # Place the second axis on the right
            "side": "right",
            # and give it a title
            "title": "Second y axis",
        },
        "legend": {
            # Place the legend above chart
            "yanchor": "bottom"
        },
    }

    page = """
# Basics - Multiple axis

Shared axis:
<|{data}|chart|x=x|y[1]=y1|y[2]=y2|height=300px|>

With two axis:
<|{data}|chart|x=x|y[1]=y1|y[2]=y2|yaxis[2]=y2|layout={layout}|height=300px|>
    """

    Gui(page).run()
