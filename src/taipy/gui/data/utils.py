# Copyright 2022 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

from __future__ import annotations

import typing as t

import numpy as np

from ..utils.rdp import rdp_numpy

if t.TYPE_CHECKING:
    import pandas as pd


def _df_data_filter(dataframe: pd.DataFrame, x_column_name: t.Union[None, str], y_column_name: str, epsilon: int):
    df = dataframe.copy()
    if not x_column_name:
        index = 0
        while f"tAiPy_index_{index}" in df.columns:
            index += 1
        x_column_name = f"tAiPy_index_{index}"
        df[x_column_name] = df.index
    points = df[[x_column_name, y_column_name]].to_numpy()
    mask = rdp_numpy(points, epsilon=epsilon)
    return df[mask]
