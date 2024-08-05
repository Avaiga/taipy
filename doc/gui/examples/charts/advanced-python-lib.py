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
# This script needs to run in a Python environment where the plotly-express package is
# installed.
# -----------------------------------------------------------------------------------------
import numpy as np
import plotly.graph_objects as go

from taipy.gui import Gui

# Create the Plotly figure object
figure = go.Figure()

# Add trace for Normal Distribution
figure.add_trace(
    go.Violin(name="Normal", y=np.random.normal(loc=0, scale=1, size=1000), box_visible=True, meanline_visible=True)
)

# Add trace for Exponential Distribution
figure.add_trace(
    go.Violin(name="Exponential", y=np.random.exponential(scale=1, size=1000), box_visible=True, meanline_visible=True)
)

# Add trace for Uniform Distribution
figure.add_trace(
    go.Violin(name="Uniform", y=np.random.uniform(low=0, high=1, size=1000), box_visible=True, meanline_visible=True)
)

# Updating layout for better visualization
figure.update_layout(title="Different Probability Distributions")

page = """
<|chart|figure={figure}|>
"""

Gui(page).run()
