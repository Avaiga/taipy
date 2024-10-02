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

from __future__ import annotations

import typing as t
from enum import Enum
from inspect import isclass
from operator import add

from .._warnings import _warn
from ..icon import Icon
from . import _MapDict


class _AdaptedLov:
    def __init__(self, lov: t.Any, var_type: str) -> None:
        self._lov = lov
        self._type = var_type

    @staticmethod
    def get_lov(lov: t.Any):
        return lov._lov if isinstance(lov, _AdaptedLov) else lov

    @staticmethod
    def get_type(lov: t.Any):
        return lov._type if isinstance(lov, _AdaptedLov) else None


class _Adapter:
    def __init__(self) -> None:
        self.__adapter_for_type: t.Dict[str, t.Callable] = {}
        self.__type_for_variable: t.Dict[str, str] = {}
        self.__warning_by_type: t.Set[str] = set()

    def _get_adapted_lov(self, lov: t.Any, var_type: str) -> _AdaptedLov:
        if not isinstance(lov, list) and hasattr(lov, "tolist"):
            try:
                lov = lov.tolist()  # type: ignore[union-attr]
            except Exception as e:
                _warn("Error accessing List of values", e)
        return _AdaptedLov(lov, var_type)

    def _add_for_type(self, type_name: str, adapter: t.Callable) -> None:
        self.__adapter_for_type[type_name] = adapter

    def _add_type_for_var(self, var_name: str, type_name: str) -> None:
        self.__type_for_variable[var_name] = type_name

    def _get_for_type(self, type_name: str) -> t.Optional[t.Callable]:
        return self.__adapter_for_type.get(type_name)

    def _get_unique_type(self, type_name: str) -> str:
        index = 0
        while type_name in self.__adapter_for_type:
            type_name = f"{type_name}{index}"
            index += 1
        return type_name

    def run(self, var_name: str, value: t.Any, id_only=False) -> t.Any:
        lov = _AdaptedLov.get_lov(value)
        adapter = self.__get_for_var(var_name, value)
        if isclass(lov) and issubclass(lov, Enum):
            lov = list(lov)
        if isinstance(lov, (list, tuple)):
            res = []
            for elt in lov:
                v = self._run(adapter, elt, var_name, id_only)
                res.append(v if v is not None else elt)
            return res
        return self._run(adapter, lov, var_name, id_only)

    def __get_for_var(self, var_name: str, value: t.Any) -> t.Optional[t.Callable]:
        adapter = None
        type_name = _AdaptedLov.get_type(value)
        if type_name:
            adapter = self.__adapter_for_type.get(type_name)
        if callable(adapter):
            return adapter
        type_name = self.__type_for_variable.get(var_name)
        if not isinstance(type_name, str):
            adapter = self.__adapter_for_type.get(var_name)
            lov = _AdaptedLov.get_lov(value)
            elt = lov[0] if isinstance(lov, (list, tuple)) and len(lov) else None
            type_name = var_name if callable(adapter) else type(elt).__name__
        if adapter is None:
            adapter = self.__adapter_for_type.get(type_name)
        return adapter if callable(adapter) else None

    def _get_elt_per_ids(
        self, var_name: str, lov: t.List[t.Any], adapter: t.Optional[t.Callable] = None
    ) -> t.Dict[str, t.Any]:
        dict_res = {}
        type_name = _AdaptedLov.get_type(lov)
        lov = _AdaptedLov.get_lov(lov)
        if not adapter and type_name:
            adapter = self.__adapter_for_type.get(type_name)
        if not adapter:
            adapter = self.__get_for_var(var_name, lov[0] if lov else None)
        for value in lov:
            try:
                result = adapter(value._dict if isinstance(value, _MapDict) else value) if adapter else value
                if result is not None:
                    dict_res[self.__get_id(result)] = value
                    children = self.__get_children(result)
                    if children is not None:
                        dict_res.update(self._get_elt_per_ids(var_name, children, adapter))
            except Exception as e:
                _warn(f"Cannot run adapter for {var_name}", e)
        return dict_res

    def _run(
        self, adapter: t.Optional[t.Callable], value: t.Any, var_name: str, id_only=False
    ) -> t.Union[t.Tuple[str, ...], str, None]:
        if value is None:
            return None
        try:
            result = value._dict if isinstance(value, _MapDict) else value
            if adapter:
                result = adapter(result)
                if result is None:
                    return result
            elif isinstance(result, (str, float, int)):
                return str(result)
            tpl_res = self._get_valid_result(result, id_only)
            if tpl_res is None:
                _warn(
                    f"Adapter for {var_name} did not return a valid result. Please check the documentation on List of Values Adapters."  # noqa: E501
                )
            else:
                if not id_only and len(tpl_res) > 2 and isinstance(tpl_res[2], list) and len(tpl_res[2]) > 0:
                    tpl_res = (tpl_res[0], tpl_res[1], self.__on_tree(adapter, tpl_res[2]))
                return (
                    add(type(result)(tpl_res), result[len(tpl_res) :])
                    if isinstance(result, (tuple, list)) and isinstance(tpl_res, (tuple, list))
                    else tpl_res # type: ignore[reportReturnType]
                )
        except Exception as e:
            _warn(f"Cannot run adapter for {var_name}", e)
        return None

    def __on_tree(self, adapter: t.Optional[t.Callable], tree: t.List[t.Any]):
        ret_list = []
        for elt in tree:
            ret = self._run(adapter, elt, adapter.__name__ if adapter else "adapter")
            if ret is not None:
                ret_list.append(ret)
        return ret_list

    def _get_valid_result(self, value: t.Any, id_only=False) -> t.Union[t.Tuple[str, ...], str, None]:
        id = self.__get_id(value)
        if id_only:
            return id
        label = self.__get_label(value)
        if label is None:
            return None
        children = self.__get_children(value)
        return (id, label) if children is None else (id, label, children)  # type: ignore

    def __get_id(self, value: t.Any, dig=True) -> str:
        if isinstance(value, str):
            return value
        elif dig:
            if isinstance(value, (list, tuple)) and len(value):
                return self.__get_id(value[0], False)
            elif hasattr(value, "id"):
                return self.__get_id(t.cast(t.Any, value).id, False)
            elif hasattr(value, "__getitem__") and "id" in value:
                return self.__get_id(t.cast(dict, value).get("id"), False)
        if value is not None and type(value).__name__ not in self.__warning_by_type:
            _warn(f"LoV id must be a string, using a string representation of {type(value)}.")
            self.__warning_by_type.add(type(value).__name__)
        return "" if value is None else str(value)

    def __get_label(self, value: t.Any, dig=True) -> t.Union[str, t.Dict, None]:
        if isinstance(value, (str, Icon)):
            return Icon.get_dict_or(value)
        elif dig:
            if isinstance(value, (list, tuple)) and len(value) > 1:
                return self.__get_label(value[1], False)
            elif hasattr(value, "label"):
                return self.__get_label(t.cast(t.Any, value).label, False)
            elif hasattr(value, "__getitem__") and "label" in value:
                return self.__get_label(t.cast(dict, value).get("label"), False)
        return None

    def __get_children(self, value: t.Any) -> t.Optional[t.List[t.Any]]:
        if isinstance(value, (tuple, list)) and len(value) > 2:
            return value[2] if isinstance(value[2], list) else None if value[2] is None else [value[2]]
        elif hasattr(value, "children"):
            return (
                t.cast(t.Any, value).children
                if isinstance(t.cast(t.Any, value).children, list)
                else None
                if t.cast(t.Any, value).children is None
                else [t.cast(t.Any, value).children]
            )
        elif hasattr(value, "__getitem__") and "children" in value:
            return (
                t.cast(dict, value).get("children")
                if isinstance(t.cast(dict, value).get("children"), list)
                else None
                if t.cast(dict, value).get("children") is None
                else [t.cast(dict, value).get("children")]
            )
        return None
