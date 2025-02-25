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
from abc import abstractmethod

import pandas as pd

from .data_accessor import _DataAccessor
from .data_format import _DataFormat
from .pandas_data_accessor import _PandasDataAccessor


class _PandasBasedDataAccessor(_DataAccessor):
    def __init__(self, gui) -> None:
        super().__init__(gui)
        self.__accessor_instance: t.Optional[_PandasDataAccessor] = None

    def _get_pandas_accessor(self):
        if self.__accessor_instance is None:
            self.__accessor_instance = self._gui._get_accessor()._get_instance(pd.DataFrame({}))  # type: ignore[arg-type, assignment]
        return t.cast(_PandasDataAccessor, self.__accessor_instance)

    @abstractmethod
    def _from_pandas(self, value: pd.DataFrame, data_type: t.Type) -> t.Any:
        pass

    def get_cols_description(self, var_name: str, value: t.Any) -> t.Union[None, t.Dict[str, t.Dict[str, str]]]:  # type: ignore
        return self._get_pandas_accessor().get_cols_description(var_name, self.to_pandas(value))

    def get_data(
        self, var_name: str, value: t.Any, payload: t.Dict[str, t.Any], data_format: _DataFormat
    ) -> t.Dict[str, t.Any]:
        return self._get_pandas_accessor().get_data(var_name, self.to_pandas(value), payload, data_format)

    def on_edit(self, value: t.Any, payload: t.Dict[str, t.Any]) -> t.Optional[t.Any]:
        return self._from_pandas(self._get_pandas_accessor().on_edit(self.to_pandas(value), payload), type(value))

    def on_delete(self, value: t.Any, payload: t.Dict[str, t.Any]) -> t.Optional[t.Any]:
        return self._from_pandas(self._get_pandas_accessor().on_delete(self.to_pandas(value), payload), type(value))

    def on_add(
        self, value: t.Any, payload: t.Dict[str, t.Any], new_row: t.Optional[t.List[t.Any]] = None
    ) -> t.Optional[t.Any]:
        return self._from_pandas(
            self._get_pandas_accessor().on_add(self.to_pandas(value), payload, new_row), type(value)
        )

    def to_csv(self, var_name: str, value: t.Any) -> t.Optional[str]:
        return self._get_pandas_accessor().to_csv(var_name, self.to_pandas(value))
