from __future__ import annotations

import typing as t
import warnings
from types import FunctionType

import __main__

from ..taipyimage import TaipyImage
from . import _get_dict_value, _MapDictionary


class _Adapter:
    def __init__(self):
        self.__adapter_for_type: t.Dict[str, FunctionType] = {}
        self.__type_for_variable: t.Dict[str, str] = {}
        self.__list_for_variable: t.Dict[str, str] = {}

    def _add_list_for_variable(self, var_name: str, list_name: str) -> None:
        self.__list_for_variable[var_name] = list_name

    def _add_adapter_for_type(self, type_name: str, adapter: FunctionType) -> None:
        self.__adapter_for_type[type_name] = adapter

    def _add_type_for_var(self, var_name: str, type_name: str) -> None:
        self.__type_for_variable[var_name] = type_name

    def _get_adapter_for_type(self, type_name: str) -> t.Optional[FunctionType]:
        return _get_dict_value(self.__adapter_for_type, type_name)

    def _run_adapter_for_var(self, var_name: str, value: t.Any, index: t.Optional[str] = None, id_only=False) -> t.Any:
        adapter = None
        type_name = _get_dict_value(self.__type_for_variable, var_name)
        if not isinstance(type_name, str):
            adapter = _get_dict_value(self.__adapter_for_type, var_name)
            if isinstance(adapter, FunctionType):
                type_name = var_name
            else:
                type_name = type(value).__name__
        if adapter is None:
            adapter = _get_dict_value(self.__adapter_for_type, type_name)
        if isinstance(adapter, FunctionType):
            ret = self._run_adapter(adapter, value, var_name, index, id_only)
            if ret is not None:
                return ret
        return value

    def _run_adapter(
        self, adapter: FunctionType, value: t.Any, var_name: str, index: t.Optional[str], id_only=False
    ) -> t.Union[t.Tuple[str, ...], str, None]:
        if value is None:
            return None
        try:
            result = adapter(value if not isinstance(value, _MapDictionary) else value._dict)
            result = self._get_valid_adapter_result(result, index, id_only)
            if result is None:
                warnings.warn(
                    f"Adapter for {var_name} does not return a valid result. It should return a tuple (id, label) or a label with label being a string or a TaipyImage instance"
                )
            else:
                if not id_only and len(result) > 2 and isinstance(result[2], list):
                    result = (result[0], result[1], self.__adapter_on_tree(adapter, result[2], str(index) + "."))
                return result
        except Exception as e:
            warnings.warn(f"Can't run adapter for {var_name}: {e}")
        return None

    def __adapter_on_tree(self, adapter: FunctionType, tree: t.List[t.Any], prefix: str):
        ret_list = []
        for idx, elt in enumerate(tree):
            ret = self._run_adapter(adapter, elt, adapter.__name__, prefix + str(idx))
            if ret is not None:
                if len(ret) > 2 and isinstance(ret[2], list):
                    ret = (ret[0], ret[1], self.__adapter_on_tree(adapter, ret[2], prefix + str(idx) + "."))
                ret_list.append(ret)
        return ret_list

    def _get_valid_adapter_result(
        self, value: t.Any, index: t.Optional[str], id_only=False
    ) -> t.Union[tuple[str, t.Union[str, TaipyImage]], str, None]:
        if (
            isinstance(value, tuple)
            and len(value) > 1
            and isinstance(value[0], str)
            and isinstance(value[1], (str, TaipyImage))
        ):
            if id_only:
                return value[0]
            elif len(value) > 2 and isinstance(value[2], list):
                return (value[0], TaipyImage.get_dict_or(value[1]), value[2])  # type: ignore
            else:
                return (value[0], TaipyImage.get_dict_or(value[1]))  # type: ignore
        else:
            id = self.__get_id(value, index)
            if id_only:
                return id
            label = self.__get_label(value)
            if label is None:
                return None
            if len(value) > 2 and isinstance(value[2], list):
                return (id, label, self.__get_children(value))  # type: ignore
            else:
                return (id, label)  # type: ignore

    def __get_id(self, value: t.Any, index: t.Optional[str]) -> str:
        if hasattr(value, "id"):
            return str(value.id)
        elif hasattr(value, "__getitem__") and "id" in value:
            return str(value["id"])
        elif index is not None:
            return index
        else:
            return str(id(value))

    def __get_label(self, value: t.Any) -> t.Union[str, t.Dict, None]:
        if isinstance(value, (str, TaipyImage)):
            return TaipyImage.get_dict_or(value)
        elif hasattr(value, "label"):
            return TaipyImage.get_dict_or(value.label)
        elif hasattr(value, "__getitem__") and "label" in value:
            return TaipyImage.get_dict_or(value["label"])
        return None

    def __get_children(self, value: t.Any) -> t.List[t.Any]:
        if isinstance(value, list):
            return value
        elif hasattr(value, "children"):
            return value.children if isinstance(value.children, list) else [value.children]
        elif hasattr(value, "__getitem__") and "children" in value:
            return value["children"] if isinstance(value["children"], list) else [value["children"]]
        return []
