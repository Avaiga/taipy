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

# Skill categories
skills = ["HTML", "CSS", "Java", "Python", "PHP", "JavaScript", "Photoshop"]
data = [
    # Proportion of skills used for Backend development
    {"Backend": [10, 10, 80, 70, 90, 30, 0], "Skills": skills},
    # Proportion of skills used for Frontend development
    {"Frontend": [90, 90, 0, 10, 20, 80, 60], "Skills": skills},
]

# Append first elements to all arrays for a nice stroke
skills.append(skills[0])
data[0]["Backend"].append(data[0]["Backend"][0])
data[1]["Frontend"].append(data[1]["Frontend"][0])

layout = {
    # Force the radial axis displayed range
    "polar": {"radialaxis": {"range": [0, 100]}}
}

# Fill the trace
options = {"fill": "toself"}

# Reflected in the legend
names = ["Backend", "Frontend"]

# To shorten the chart control definition
r = ["0/Backend", "1/Frontend"]
theta = ["0/Skills", "1/Skills"]

page = """
# Radar - Multiple

<|{data}|chart|type=scatterpolar|name={names}|r={r}|theta={theta}|options={options}|layout={layout}|>
"""

Gui(page).run()
