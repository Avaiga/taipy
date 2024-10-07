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
from enum import Enum

import numpy as np
import pandas as pd

from taipy.gui import Gui
from taipy.gui.data.decimator import MinMaxDecimator


# Processing techniques
class Processing(Enum):
    # Don't process the data
    NONE = 0
    # Sub-sample the dataset
    SUB_SAMPLING = 1
    # Compute local average in the dataset
    AVERAGE = 2
    # Use decimation
    DECIMATION = 3


# Choose a processing technique
processing = Processing.DECIMATION

# Generate a random dataset
#   Compute the 'X' data
#     Generate 50000 x values (a sequence of integers)
x_values = np.linspace(1, 100, 50000)

#   Compute the 'Y' data
#     Define the combined log-sine function
y_values = np.log(x_values) * np.sin(x_values / 5)
#   Introduce some noise
#     Create a mask with a True value with a 1 % probability
noise_mask = np.random.rand(*y_values.shape) < 0.01
#     The noise values
noise_values = np.random.uniform(-0.5, 0.5, size=np.sum(noise_mask))
#     Add the noise to the 'Y' values
y_values_noise = np.copy(y_values)  # Copy original array
y_values_noise[noise_mask] += noise_values

# Use no decimator by default
decimator = None

# Transform the 'Y' dataset with the chosen processing technique
if processing == Processing.SUB_SAMPLING:
    # Pick one every 100 data points
    x_values = x_values[::100]
    y_values_noise = y_values_noise[::100]

elif processing == Processing.AVERAGE:
    # Average of 100 successive values
    x_values = x_values[::100]
    y_values_noise = y_values_noise.reshape(-1, 100)
    # Compute the average of each group of 100 values
    y_values_noise = np.mean(y_values_noise, axis=1)

elif processing == Processing.DECIMATION:
    # Use Taipy's decimation processing
    decimator = MinMaxDecimator(200)

print(f"Using {str(processing)}: Dataset has {y_values_noise.size} data points")

# Create the DataFrame
data = pd.DataFrame({"X": x_values, "Y": y_values_noise})

page = "<|{data}|chart|x=X|y=Y|mode=lines|decimator=decimator|>"

if __name__ == "__main__":
    Gui(page).run(title="Chart - Advanced - Large datasets")
