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
from abc import ABC, abstractmethod

import numpy as np

if t.TYPE_CHECKING:
    import pandas as pd


class Decimator(ABC):
    def __init__(self, applied_threshold: t.Optional[int]) -> None:
        """TODO: Decimator class description"""
        self.applied_threshold = applied_threshold
        super().__init__()

    def _is_applicable(self, data: t.Any, nb_rows_max: int):
        if self.applied_threshold is None:
            if nb_rows_max < len(data):
                return True
        elif self.applied_threshold < len(data):
            return True
        return False

    @abstractmethod
    def decimate(self, data: np.ndarray) -> np.ndarray:
        """Decimate function for decimator. This function will be executed during runtime when the appropriate conditions
        are met.
        TODO: Further explanation

        Arguments:
            data (numpy.array): A 2-dimensional array. This will be provided by taipy
            during runtime

        Returns:
            A boolean mask array for the original data
        """
        return NotImplemented


def _df_data_filter(
    dataframe: pd.DataFrame, x_column_name: t.Union[None, str], y_column_name: str, decimator: Decimator
):
    df = dataframe.copy()
    if not x_column_name:
        index = 0
        while f"tAiPy_index_{index}" in df.columns:
            index += 1
        x_column_name = f"tAiPy_index_{index}"
        df[x_column_name] = df.index
    points = df[[x_column_name, y_column_name]].to_numpy()
    mask = decimator.decimate(points)
    return df[mask]
