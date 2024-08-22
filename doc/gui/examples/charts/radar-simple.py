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
from typing import Dict, List

from taipy.gui import Gui

if __name__ == "__main__":
    # Source: www.statista.com (Most used programming languages in 2022)
    data: Dict[str, List] = {
        # List of programming languages
        "Language": ["JavaScript", "HTML/CSS", "SQL", "Python", "Typescript", "Java", "Bash/Shell"],
        # Percentage of usage, per language
        "%": [65.36, 55.08, 49.43, 48.07, 34.83, 33.27, 29.07],
    }

    # Close the shape for a nice-looking stroke
    # If the first point is *not* appended to the end of the list,
    # then the shape does not look as it is closed.
    data["%"].append(data["%"][0])
    data["Language"].append(data["Language"][0])

    layout = {
        "polar": {
            "radialaxis": {
                # Force the radial range to 0-100
                "range": [0, 100],
            }
        },
        # Hide legend
        "showlegend": False,
    }

    options = {
        # Fill the trace
        "fill": "toself"
    }

    md = """
# Radar - Simple

<|{data}|chart|type=scatterpolar|r=%|theta=Language|options={options}|layout={layout}|>
    """

    Gui(md).run()
