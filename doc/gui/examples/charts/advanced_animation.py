# Copyright 2021-2025 Avaiga Private Limited
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
from math import ceil, cos

from taipy.gui import Gui

# Available waveforms to choose from
waveforms = ["Sine", "Square"]
# The initially selected waveform
waveform = waveforms[0]

# Values for the x axis
x_range = range(100)
# Data for the 'Sine' waveform
cos_data = [cos(i / 6) for i in x_range]
# Data for the 'Square' waveform
square_data = [1 if ceil(i / 24) % 2 == 0 else -1 for i in x_range]

# Dataset used by the chart
data = {
    "x": x_range,
    "y": cos_data,
}

animation_data = None


# Triggered when the selected waveform changes
def change_data(state):
    # Animate by setting the 'y' values to the selected waveform's
    state.animation_data = {"y": cos_data if state.waveform == waveforms[0] else square_data}


page = """
<|{waveform}|toggle|lov={waveforms}|on_change=change_data|>
<|{data}|chart|mode=lines+markers|x=x|y=y|animation_data={animation_data}|>
"""


if __name__ == "__main__":
    Gui(page).run(title="Chart - Advanced - Animation")
