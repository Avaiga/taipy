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
# You may need to install the scikit-learn package as well.
# -----------------------------------------------------------------------------------------
import numpy
import pandas
from sklearn.datasets import make_classification

from taipy.gui import Gui

# Let scikit-learn generate a random 2-class classification problem
features, label = make_classification(n_samples=1000, n_features=2, n_informative=2, n_redundant=0)

random_data = pandas.DataFrame({"x": features[:, 0], "y": features[:, 1], "label": label})

data_x = random_data["x"]
class_A = [
    random_data.loc[i, "y"] if random_data.loc[i, "label"] == 0 else numpy.nan for i in range(len(random_data))
]
class_B = [
    random_data.loc[i, "y"] if random_data.loc[i, "label"] == 1 else numpy.nan for i in range(len(random_data))
]

data = {"x": random_data["x"], "Class A": class_A, "Class B": class_B}

page = """
<|{data}|chart|mode=markers|x=x|y[1]=Class A|y[2]=Class B|width=60%|>
"""

if __name__ == "__main__":
    Gui(page).run(title="Chart - Scatter - Classification")
