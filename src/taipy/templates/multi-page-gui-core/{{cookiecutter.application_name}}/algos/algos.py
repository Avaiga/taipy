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

import numpy as np
from sklearn.linear_model import LinearRegression


def clean_data(data):
    ...
    return data.dropna().drop_duplicates()


def predict(data):
    model = LinearRegression()
    model.fit(data[["x"]], data[["y"]])
    data["y_pred"] = model.predict(data[["x"]])
    return data


def evaluate(data):
    ...
    return np.random.rand()
