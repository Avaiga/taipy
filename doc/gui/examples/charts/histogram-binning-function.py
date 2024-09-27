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

# Initial data set. y = count_of(x)
samples = {"x": ["Apples", "Apples", "Apples", "Oranges", "Bananas", "Oranges"], "y": [5, 10, 3, 8, 5, 2]}

# Create a data set array to allow for two traces
data = [samples, samples]

# Gather those settings in a single dictionary
properties = {
    # 'x' of the first trace is the 'x' data from the first element of data
    "x[1]": "0/x",
    # 'y' of the first trace is the 'y' data from the first element of data
    "y[1]": "0/y",
    # 'x' of the second trace is the 'x' data from the second element of data
    "x[2]": "1/x",
    # 'y' of the second trace is the 'y' data from the second element of data
    "y[2]": "1/y",
    # Data set colors
    "color": ["#cd5c5c", "#505070"],
    # Data set names (for the legend)
    "name": ["Count", "Sum"],
    # Configure the binning functions
    "options": [
        # First trace: count the bins
        {"histfunc": "count"},
        # Second trace: sum the bin occurrences
        {"histfunc": "sum"},
    ],
    # Set x axis name
    "layout": {"xaxis": {"title": "Fruit"}},
}

page = """
<|{data}|chart|type=histogram|properties={properties}|>
"""

if __name__ == "__main__":
    Gui(page).run(title="Chart - Histogram - Binning function")
