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

import inspect
import typing as t
from abc import ABC, abstractmethod

from .._warnings import _warn
from ..utils import _TaipyData
from .data_format import _DataFormat

if t.TYPE_CHECKING:
    from ..gui import Gui


class _DataAccessor(ABC):
    _WS_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"

    def __init__(self, gui: "Gui") -> None:
        self._gui = gui

    @staticmethod
    @abstractmethod
    def get_supported_classes() -> t.List[t.Type]:
        pass

    @abstractmethod
    def get_data(
        self, var_name: str, value: t.Any, payload: t.Dict[str, t.Any], data_format: _DataFormat
    ) -> t.Dict[str, t.Any]:
        pass

    @abstractmethod
    def get_col_types(self, var_name: str, value: t.Any) -> t.Dict[str, str]:
        pass

    @abstractmethod
    def to_pandas(self, value: t.Any) -> t.Union[t.List[t.Any], t.Any]:
        pass

    @abstractmethod
    def on_edit(self, value: t.Any, payload: t.Dict[str, t.Any]) -> t.Optional[t.Any]:
        pass

    @abstractmethod
    def on_delete(self, value: t.Any, payload: t.Dict[str, t.Any]) -> t.Optional[t.Any]:
        pass

    @abstractmethod
    def on_add(
        self, value: t.Any, payload: t.Dict[str, t.Any], new_row: t.Optional[t.List[t.Any]] = None
    ) -> t.Optional[t.Any]:
        pass

    @abstractmethod
    def to_csv(self, var_name: str, value: t.Any) -> t.Optional[str]:
        pass


class _InvalidDataAccessor(_DataAccessor):
    @staticmethod
    def get_supported_classes() -> t.List[t.Type]:
        return []

    def get_data(
        self, var_name: str, value: t.Any, payload: t.Dict[str, t.Any], data_format: _DataFormat
    ) -> t.Dict[str, t.Any]:
        return {}

    def get_col_types(self, var_name: str, value: t.Any) -> t.Dict[str, str]:
        return {}

    def to_pandas(self, value: t.Any) -> t.Union[t.List[t.Any], t.Any]:
        return None

    def on_edit(self, value: t.Any, payload: t.Dict[str, t.Any]):
        return None

    def on_delete(self, value: t.Any, payload: t.Dict[str, t.Any]):
        return None

    def on_add(self, value: t.Any, payload: t.Dict[str, t.Any], new_row: t.Optional[t.List[t.Any]] = None):
        return None

    def to_csv(self, var_name: str, value: t.Any):
        return None


class _DataAccessors(object):
    def __init__(self, gui: "Gui") -> None:
        self.__access_4_type: t.Dict[t.Type, _DataAccessor] = {}
        self.__invalid_data_accessor = _InvalidDataAccessor(gui)
        self.__data_format = _DataFormat.JSON
        self.__gui = gui

        from .array_dict_data_accessor import _ArrayDictDataAccessor
        from .numpy_data_accessor import _NumpyDataAccessor
        from .pandas_data_accessor import _PandasDataAccessor

        self._register(_PandasDataAccessor)
        self._register(_ArrayDictDataAccessor)
        self._register(_NumpyDataAccessor)

    def _register(self, cls: t.Type[_DataAccessor]) -> None:
        if not inspect.isclass(cls):
            raise AttributeError("The argument of 'DataAccessors.register' should be a class")
        if not issubclass(cls, _DataAccessor):
            raise TypeError(f"Class {cls.__name__} is not a subclass of DataAccessor")
        classes = cls.get_supported_classes()
        if not classes:
            raise TypeError(f"method {cls.__name__}.get_supported_classes returned an invalid value")
        # check existence
        inst: t.Optional[_DataAccessor] = None
        for cl in classes:
            inst = self.__access_4_type.get(cl)
            if inst:
                break
        if inst is None:
            try:
                inst = cls(self.__gui)
            except Exception as e:
                raise TypeError(f"Class {cls.__name__} cannot be instantiated") from e
            if inst:
                for cl in classes:
                    self.__access_4_type[cl] = inst  # type: ignore

    def __get_instance(self, value: _TaipyData) -> _DataAccessor:  # type: ignore
        value = value.get() if isinstance(value, _TaipyData) else value
        access = self.__access_4_type.get(type(value))
        if access is None:
            if value is not None:
                _warn(f"Can't find Data Accessor for type {str(type(value))}.")
            return self.__invalid_data_accessor
        return access

    def get_data(self, var_name: str, value: _TaipyData, payload: t.Dict[str, t.Any]) -> t.Dict[str, t.Any]:
        return self.__get_instance(value).get_data(var_name, value.get(), payload, self.__data_format)

    def get_col_types(self, var_name: str, value: _TaipyData) -> t.Dict[str, str]:
        return self.__get_instance(value).get_col_types(var_name, value.get())

    def set_data_format(self, data_format: _DataFormat):
        self.__data_format = data_format

    def get_dataframe(self, value: t.Any):
        return self.__get_instance(value).to_pandas(value)

    def on_edit(self, value: t.Any, payload: t.Dict[str, t.Any]):
        return self.__get_instance(value).on_edit(value, payload)

    def on_delete(self, value: t.Any, payload: t.Dict[str, t.Any]):
        return self.__get_instance(value).on_delete(value, payload)

    def on_add(self, value: t.Any, payload: t.Dict[str, t.Any], new_row: t.Optional[t.List[t.Any]] = None):
        return self.__get_instance(value).on_add(value, payload, new_row)

    def to_csv(self, var_name: str, value: t.Any):
        return self.__get_instance(value).to_csv(var_name, value.get())

    def to_pandas(self, value: t.Any):
        return self.__get_instance(value).to_pandas(value.get())
