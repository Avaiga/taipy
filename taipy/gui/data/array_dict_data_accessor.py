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

import typing as t

import pandas as pd

from ..utils import _MapDict
from .data_format import _DataFormat
from .pandas_data_accessor import _PandasDataAccessor


class _ArrayDictDataAccessor(_PandasDataAccessor):
    __types = (dict, list, tuple, _MapDict)

    @staticmethod
    def get_supported_classes() -> t.List[t.Type]:
        return list(_ArrayDictDataAccessor.__types)

    def to_pandas(self, value: t.Any) -> t.Union[t.List[pd.DataFrame], pd.DataFrame]:
        if isinstance(value, (list, tuple)):
            if not value or isinstance(value[0], (str, int, float, bool)):
                return pd.DataFrame({"0": value})
            types = {type(x) for x in value}
            if len(types) == 1:
                type_elt = next(iter(types), None)
                if type_elt is list:
                    lengths = {len(x) for x in value}
                    return (
                        pd.DataFrame(value)
                        if len(lengths) == 1
                        else [pd.DataFrame({f"{i}/0": v}) for i, v in enumerate(value)]
                    )
                elif type_elt is dict:
                    return [pd.DataFrame(v) for v in value]
                elif type_elt is _MapDict:
                    return [pd.DataFrame(v._dict) for v in value]
                elif type_elt is pd.DataFrame:
                    return t.cast(t.List[pd.DataFrame], value)

            elif len(types) == 2 and list in types and pd.DataFrame in types:
                return [v if isinstance(v, pd.DataFrame) else pd.DataFrame({f"{i}/0": v}) for i, v in enumerate(value)]
        elif isinstance(value, _MapDict):
            return pd.DataFrame(value._dict)
        return pd.DataFrame(value)

    def _from_pandas(self, value: pd.DataFrame, data_type: t.Type):
        if data_type is dict:
            return value.to_dict("list")
        if data_type is _MapDict:
            return _MapDict(value.to_dict("list"))
        if len(value.columns) == 1:
            if data_type is list:
                return value.iloc[:, 0].to_list()
            if data_type is tuple:
                return tuple(value.iloc[:, 0].to_list())
        return super()._from_pandas(value, data_type)

    def get_col_types(self, var_name: str, value: t.Any) -> t.Union[None, t.Dict[str, str]]:  # type: ignore
        return super().get_col_types(var_name, self.to_pandas(value))

    def get_data(  # noqa: C901
        self, var_name: str, value: t.Any, payload: t.Dict[str, t.Any], data_format: _DataFormat
    ) -> t.Dict[str, t.Any]:
        return super().get_data(var_name, self.to_pandas(value), payload, data_format)
