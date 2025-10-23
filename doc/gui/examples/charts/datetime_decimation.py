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
"""
Example demonstrating proper use of decimators with datetime data.

This example shows how to handle datetime data with MinMaxDecimator by using
numeric x-axis values while keeping datetime information separate.
"""

from datetime import datetime

import numpy as np
import pandas as pd

import taipy.gui.builder as tgb
from taipy.gui import Gui
from taipy.gui.data.decimator import MinMaxDecimator

# Create sample datetime data
x_values = np.linspace(1, 100, 50000)
y_values = np.log(x_values) * np.sin(x_values / 5)
noise_mask = np.random.rand(*y_values.shape) < 0.01
noise_values = np.random.uniform(-0.5, 0.5, size=np.sum(noise_mask))
y_values_noise = np.copy(y_values)
y_values_noise[noise_mask] += noise_values

# How to decimate datetime data? - Structure data for decimation algorithm:
# Column 0: Numeric values for decimation algorithm (data[:, 0])
# Column 1: Y values (data[:, 1])
# Column 2: DateTime values for x-axis display (data[:, 2])
start_time = datetime.now()
timestamps = [start_time + pd.Timedelta(seconds=x) for x in x_values]

data = pd.DataFrame({"X_numeric": x_values, "Y": y_values_noise, "X_datetime": timestamps})

decimator = MinMaxDecimator(200)

if __name__ == "__main__":
    with tgb.Page() as page:
        tgb.chart(
            "{data}",
            type="markers",
            x="X_datetime",  # Show datetime on x-axis
            y="Y",
            decimator=decimator,
        )

        tgb.text("Data Preview")
        tgb.table("{data.head(10)}")

    gui = Gui(page=page)
    gui.run(port=5010, title="Chart - DateTime Decimation")
