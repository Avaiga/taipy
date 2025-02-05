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

import typing as t

import numpy
import pandas as pd

from .pandas_based_data_accessor import _PandasBasedDataAccessor


class _NumpyDataAccessor(_PandasBasedDataAccessor):
    __types = (numpy.ndarray,)

    @staticmethod
    def get_supported_classes() -> t.List[t.Type]:
        return list(_NumpyDataAccessor.__types)

    def to_pandas(self, value: t.Any) -> pd.DataFrame:
        return pd.DataFrame(value)

    def _from_pandas(self, value: pd.DataFrame, data_type: t.Type):
        if data_type is numpy.ndarray:
            return value.to_numpy()
        return self._get_pandas_accessor()._from_pandas(value, data_type)
