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

from sklearn.datasets import make_regression
from sklearn.linear_model import LinearRegression

from taipy.gui import Gui

# Let scikit-learn generate a random regression problem
n_samples = 300
X, y, coef = make_regression(n_samples=n_samples, n_features=1, n_informative=1, n_targets=1, noise=25, coef=True)

model = LinearRegression().fit(X, y)

x_data = X.flatten()
y_data = y.flatten()
predict = model.predict(X)

data = {"x": x_data, "y": y_data, "Regression": predict}

page = """
# Scatter - Regression

<|{data}|chart|x=x|y[1]=y|mode[1]=markers|y[2]=Regression|mode[2]=line|>
"""

Gui(page).run()
