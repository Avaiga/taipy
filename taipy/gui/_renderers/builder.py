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

import contextlib
import json
import numbers
import time as _time
import typing as t
import xml.etree.ElementTree as etree
from datetime import date, datetime, time
from enum import Enum
from inspect import isclass, isroutine
from types import LambdaType
from urllib.parse import quote

from .._warnings import _warn
from ..partial import Partial
from ..types import PropertyType, _get_taipy_type
from ..utils import (
    _date_to_string,
    _get_broadcast_var_name,
    _get_client_var_name,
    _get_data_type,
    _get_expr_var_name,
    _get_lambda_id,
    _getscopeattr,
    _getscopeattr_drill,
    _is_boolean,
    _is_true,
    _MapDict,
    _to_camel_case,
)
from ..utils.chart_config_builder import _CHART_NAMES, _build_chart_config
from ..utils.table_col_builder import _enhance_columns, _get_name_indexed_property
from ..utils.types import _TaipyBase, _TaipyData, _TaipyToJson
from .json import _TaipyJsonEncoder
from .utils import _add_to_dict_and_get, _get_columns_dict, _get_tuple_val

if t.TYPE_CHECKING:
    from ..gui import Gui


class _Builder:
    """
    Constructs an XML node that can be rendered as a React node.

    This class can only be instantiated internally by Taipy.
    """

    __keys: t.Dict[str, int] = {}

    __BLOCK_CONTROLS = ["dialog", "expandable", "pane", "part"]

    __TABLE_COLUMNS_DEPS = [
        "data",
        "columns",
        "date_format",
        "number_format",
        "nan_value",
        "width",
        "filter",
        "editable",
        "group_by",
        "apply",
        "style",
        "tooltip",
        "lov",
    ]

    def __init__(
        self,
        gui: "Gui",
        control_type: str,
        element_name: str,
        attributes: t.Optional[t.Dict[str, t.Any]],
        hash_names: t.Optional[t.Dict[str, str]] = None,
        default_value: t.Optional[t.Any] = "<Empty>",
        lib_name: str = "taipy",
    ):
        from ..gui import Gui
        from .factory import _Factory

        if hash_names is None:
            hash_names = {}

        self.el = etree.Element(element_name)

        self.__control_type = control_type
        self.__element_name = element_name
        self.__lib_name = lib_name
        self.__attributes = attributes or {}
        self.__hashes = hash_names.copy()
        self.__update_vars: t.List[str] = []
        self.__gui: Gui = gui

        self.__default_property_name = _Factory.get_default_property_name(control_type) or ""
        default_property_value = self.__attributes.get(self.__default_property_name, None)
        if default_property_value is None and default_value is not None:
            self.__attributes[self.__default_property_name] = default_value

        # Bind properties dictionary to attributes if condition is matched (will
        # leave the binding for function at the builder )
        if "properties" in self.__attributes:
            (prop_dict, prop_hash) = _Builder.__parse_attribute_value(gui, self.__attributes["properties"])
            if prop_hash is None:
                prop_hash = prop_dict
                prop_hash = self.__gui._bind_var(prop_hash)
                if hasattr(self.__gui._bindings(), prop_hash):
                    prop_dict = _getscopeattr(self.__gui, prop_hash)
            if isinstance(prop_dict, (dict, _MapDict)):
                # Iterate through prop_dict and append to self.attributes
                var_name, _ = gui._get_real_var_name(prop_hash)
                for k, v in prop_dict.items():
                    (val, key_hash) = _Builder.__parse_attribute_value(gui, v)
                    self.__attributes[k] = (
                        f"{{None if ({var_name}) is None else ({var_name}).get('{k}')}}" if key_hash is None else v
                    )
            else:
                _warn(f"{self.__control_type}.properties ({prop_hash}) must be a dict.")

        # Bind potential function and expressions in self.attributes
        self.__hashes.update(_Builder._get_variable_hash_names(gui, self.__attributes, hash_names))

        # set classname
        self.__set_class_names()
        # define a unique key
        self.set_attribute("key", _Builder._get_key(self.__element_name))

    @staticmethod
    def __parse_attribute_value(gui: "Gui", value) -> t.Tuple:
        if isinstance(value, str) and gui._is_expression(value):
            hash_value = gui._evaluate_expr(value)
            try:
                func = gui._get_user_function(hash_value)
                if isroutine(func):
                    return (func, hash_value)
                return (_getscopeattr_drill(gui, hash_value), hash_value)
            except AttributeError:
                _warn(f"Expression '{value}' cannot be evaluated.")
        return (value, None)

    @staticmethod
    def _get_variable_hash_names(
        gui: "Gui", attributes: t.Dict[str, t.Any], hash_names: t.Optional[t.Dict[str, str]] = None
    ) -> t.Dict[str, str]:
        if hash_names is None:
            hash_names = {}
        hashes = {}
        # Bind potential function and expressions in self.attributes
        for k, v in attributes.items():
            hash_name = hash_names.get(k)
            if hash_name is None:
                if isinstance(v, str):
                    looks_like_a_lambda = v.startswith("{lambda ") and v.endswith("}")
                    # need to unescape the double quotes that were escaped during preprocessing
                    (val, hash_name) = _Builder.__parse_attribute_value(gui, v.replace('\\"', '"'))
                else:
                    looks_like_a_lambda = False
                    val = v
                if isroutine(val):
                    # if it's not a callable (and not a string), forget it
                    if val.__name__ == "<lambda>":
                        # if it is a lambda and it has already a hash_name, we're fine
                        if looks_like_a_lambda or not hash_name:
                            hash_name = _get_lambda_id(t.cast(LambdaType, val))
                            gui._bind_var_val(hash_name, val)  # type: ignore[arg-type]
                    elif not hash_name:
                        hash_name = _get_expr_var_name(val.__name__)

                if val is not None or hash_name:
                    attributes[k] = val
                if hash_name:
                    hashes[k] = hash_name
        return hashes

    @staticmethod
    def __to_string(x: t.Any) -> str:
        return str(x)

    @staticmethod
    def _get_key(name: str) -> str:
        key_index = _Builder.__keys.get(name, 0)
        _Builder.__keys[name] = key_index + 1
        return f"{name}.{key_index}"

    @staticmethod
    def _reset_key() -> None:
        _Builder.__keys = {}

    def get_name_indexed_property(self, name: str) -> t.Dict[str, t.Any]:
        """
        TODO-undocumented
        Returns all properties defined as <property name>[<named index>] as a dict.

        Arguments:

            name (str): The property name.
        """
        return _get_name_indexed_property(self.__attributes, name)

    def __get_boolean_attribute(self, name: str, default_value=False):
        bool_attr = self.__attributes.get(name, default_value)
        return _is_true(bool_attr) if isinstance(bool_attr, str) else bool(bool_attr)

    def set_boolean_attribute(self, name: str, value: bool):
        """
        TODO-undocumented
        Defines a React Boolean attribute (attr={true|false}).

        Arguments:
            name (str): The property name.
            value (bool): the boolean value.
        """
        return self.__set_react_attribute(_to_camel_case(name), value)

    def set_dict_attribute(self, name: str, default_value: t.Optional[t.Dict[str, t.Any]] = None):
        """
        TODO-undocumented
        Defines a React attribute as a stringified json dict.
        The original property can be a dict or a string formed as <key 1>:<value 1>;<key 2>:<value 2>.

        Arguments:
            name (str): The property name.
            default value (dict): used if no value is specified.
        """
        dict_attr = self.__attributes.get(name)
        if dict_attr is None:
            dict_attr = default_value
        if dict_attr is not None:
            if isinstance(dict_attr, str):
                vals = [x.strip().split(":") for x in dict_attr.split(";")]
                dict_attr = {val[0].strip(): val[1].strip() for val in vals if len(val) > 1}
            if isinstance(dict_attr, (dict, _MapDict)):
                self.__set_json_attribute(_to_camel_case(name), dict_attr)
            else:
                _warn(f"{self.__element_name}: {name} should be a dict: '{str(dict_attr)}'.")
        return self

    def set_dynamic_dict_attribute(self, name: str, default_value: t.Optional[t.Dict[str, t.Any]] = None):
        """
        TODO-undocumented
        Defines a React attribute as a stringified json dict.
        The original property can be a dict or a string formed as <key 1>:<value 1>;<key 2>:<value 2>.

        Arguments:
            name (str): The property name.
            default value (dict): used if no value is specified.
        """
        dict_attr = self.__attributes.get(name)
        if dict_attr is None:
            dict_attr = default_value
        if dict_attr is not None:
            if isinstance(dict_attr, str):
                vals = [x.strip().split(":") for x in dict_attr.split(";")]
                dict_attr = {val[0].strip(): val[1].strip() for val in vals if len(val) > 1}
            if isinstance(dict_attr, (dict, _MapDict)):
                self.__set_json_attribute(_to_camel_case("default_" + name), dict_attr)
            else:
                _warn(f"{self.__element_name}: {name} should be a dict: '{str(dict_attr)}'.")
        if dict_hash := self.__hashes.get(name):
            dict_hash = self.__get_typed_hash_name(dict_hash, PropertyType.dynamic_dict)
            prop_name = _to_camel_case(name)
            self.__update_vars.append(f"{prop_name}={dict_hash}")
            self.__set_react_attribute(prop_name, dict_hash)
        return self

    def __set_json_attribute(self, name, value):
        return self.set_attribute(name, json.dumps(value, cls=_TaipyJsonEncoder))

    def set_number_attribute(self, name: str, default_value: t.Optional[str] = None, optional: t.Optional[bool] = True):
        """
        TODO-undocumented
        Defines a React number attribute (attr={<number>}).

        Arguments:

            name (str): The property name.
            default_value (optional(str)): the default value as a string.
            optional (bool): Default to True, the property is required if False.
        """
        value = self.__attributes.get(name, default_value)
        if value is None:
            if not optional:
                _warn(f"Property {name} is required for control {self.__control_type}.")
            return self
        if isinstance(value, str):
            try:
                val = float(value)
            except ValueError:
                raise ValueError(f"Property {name} expects a number for control {self.__control_type}") from None
        elif isinstance(value, numbers.Number):
            val = value  # type: ignore
        else:
            raise ValueError(
                f"Property {name} expects a number for control {self.__control_type}, received {type(value)}"
            )
        return self.__set_react_attribute(_to_camel_case(name), val)

    def __set_string_attribute(
        self, name: str, default_value: t.Optional[str] = None, optional: t.Optional[bool] = True
    ):
        str_attr = self.__attributes.get(name, default_value)
        if str_attr is None:
            if not optional:
                _warn(f"Property {name} is required for control {self.__control_type}.")
            return self
        return self.set_attribute(_to_camel_case(name), str(str_attr))

    def __set_dynamic_date_attribute(self, var_name: str, default_value: t.Optional[str] = None):
        date_attr = self.__attributes.get(var_name, default_value)
        if date_attr is None:
            date_attr = default_value
        if isinstance(date_attr, (datetime, date, time)):
            value = _date_to_string(date_attr)
            self.set_attribute(_to_camel_case(var_name), value)
        return self

    def __set_dynamic_string_attribute(
        self,
        name: str,
        default_value: t.Optional[str] = None,
        with_update: t.Optional[bool] = False,
        dynamic_property_name: t.Optional[str] = None,
    ):
        str_val = self.__attributes.get(name, default_value)
        if str_val is not None:
            self.set_attribute(
                _to_camel_case(f"default_{name}" if dynamic_property_name is None else name), str(str_val)
            )
        if hash_name := self.__hashes.get(name):
            prop_name = _to_camel_case(name if dynamic_property_name is None else dynamic_property_name)
            if with_update:
                self.__update_vars.append(f"{prop_name}={hash_name}")
            self.__set_react_attribute(prop_name, hash_name)
        return self

    def __set_function_attribute(
        self, name: str, default_value: t.Optional[str] = None, optional: t.Optional[bool] = True
    ):
        str_attr = self.__attributes.get(name, default_value)
        if str_attr is None:
            if not optional:
                _warn(f"Property {name} is required for control {self.__control_type}.")
            return self
        elif isroutine(str_attr):
            str_attr = self.__hashes.get(name)
            if str_attr is None:
                return self
        elif _is_boolean(str_attr) and not _is_true(t.cast(str, str_attr)):
            return self.__set_react_attribute(_to_camel_case(name), False)
        elif str_attr:
            str_attr = str(str_attr)
            func = self.__gui._get_user_function(str_attr)
            if func == str_attr:
                _warn(f"{self.__control_type}.{name}: {str_attr} is not a function.")
        return self.set_attribute(_to_camel_case(name), str_attr) if str_attr else self

    def __set_string_or_number_attribute(self, name: str, default_value: t.Optional[t.Any] = None):
        attr = self.__attributes.get(name, default_value)
        if attr is None:
            return self
        if isinstance(attr, numbers.Number):
            return self.__set_react_attribute(_to_camel_case(name), attr)
        else:
            return self.set_attribute(_to_camel_case(name), attr)

    def __set_react_attribute(self, name: str, value: t.Any):
        return self.set_attribute(name, "{!" + (str(value).lower() if isinstance(value, bool) else str(value)) + "!}")

    @staticmethod
    def enum_adapter(e: t.Union[Enum, str]):
        return (e.value, e.name) if isinstance(e, Enum) else e

    def _get_lov_adapter(  # noqa: C901
        self, var_name: str, property_name: t.Optional[str] = None, multi_selection=True, with_default=True
    ):
        property_name = var_name if property_name is None else property_name
        lov_name = self.__hashes.get(var_name)
        real_var_name = self.__gui._get_real_var_name(lov_name)[0] if lov_name else None
        lov = self.__attributes.get(var_name)
        adapter: t.Any = None
        var_type: t.Optional[str] = None
        if isinstance(lov, str):
            lov = list(lov.split(";"))
        if isclass(lov) and issubclass(lov, Enum):
            adapter = _Builder.enum_adapter
            var_type = "Enum"
            lov = list(lov)
        if not isinstance(lov, list) and hasattr(lov, "tolist"):
            try:
                lov = lov.tolist()  # type: ignore[union-attr]
            except Exception as e:
                _warn(f"Error accessing List of values for '{real_var_name or property_name}'", e)
                lov = None

        default_lov: t.Optional[t.List[t.Any]] = [] if with_default or not lov_name else None

        adapter = self.__attributes.get("adapter", adapter)
        if adapter and isinstance(adapter, str):
            adapter = self.__gui._get_user_function(adapter)
        if adapter and not callable(adapter):
            _warn(f"{self.__element_name}: adapter property value is invalid.")
            adapter = None
        var_type = self.__attributes.get("type", var_type)
        if isclass(var_type):
            var_type = var_type.__name__  # type: ignore

        if isinstance(lov, list):
            if not isinstance(var_type, str):
                elt = None
                if lov:
                    elt = lov[0]
                else:
                    value = self.__attributes.get("value")
                    if isinstance(value, list):
                        if len(value) > 0:
                            elt = value[0]
                    else:
                        elt = value
                var_type = self.__gui._get_unique_type_adapter(type(elt).__name__)
            if adapter is None:
                adapter = self.__gui._get_adapter_for_type(var_type)
            elif var_type == str.__name__ and isroutine(adapter):
                var_type += (
                    _get_lambda_id(t.cast(LambdaType, adapter))
                    if adapter.__name__ == "<lambda>"
                    else _get_expr_var_name(adapter.__name__)
                )
            if lov_name:
                if adapter is None:
                    adapter = self.__gui._get_adapter_for_type(lov_name)
                else:
                    self.__gui._add_type_for_var(lov_name, t.cast(str, var_type))
            if value_name := self.__hashes.get("value"):
                if adapter is None:
                    adapter = self.__gui._get_adapter_for_type(value_name)
                else:
                    self.__gui._add_type_for_var(value_name, t.cast(str, var_type))
            if adapter is not None:
                self.__gui._add_adapter_for_type(var_type, adapter)  # type: ignore

            if default_lov is not None and lov:
                for elt in lov:
                    ret = self.__gui._run_adapter(
                        t.cast(t.Callable, adapter), elt, adapter.__name__ if isroutine(adapter) else "adapter"
                    )  # type: ignore
                    if ret is not None:
                        default_lov.append(ret)

            ret_list = []
            value = self.__attributes.get("value")
            val_list = value if isinstance(value, list) else [value]
            for val in val_list:
                ret = self.__gui._run_adapter(
                    t.cast(t.Callable, adapter),
                    val,
                    adapter.__name__ if isroutine(adapter) else "adapter",
                    id_only=True,
                )  # type: ignore
                if ret is not None:
                    ret_list.append(ret)
            if multi_selection:
                self.__set_default_value("value", ret_list)
            else:
                ret_val = ret_list[0] if len(ret_list) else ""
                if ret_val == "-1" and self.__attributes.get("unselected_value") is not None:
                    ret_val = str(self.__attributes.get("unselected_value", ""))
                self.__set_default_value("value", ret_val)

        # LoV default value
        if default_lov is not None:
            self.__set_json_attribute(_to_camel_case(f"default_{property_name}"), default_lov)

        # LoV expression binding
        if lov_name and real_var_name:
            typed_lov_hash = (
                self.__gui._evaluate_expr(
                    f"{{{self.__gui._get_call_method_name('_get_adapted_lov')}({real_var_name},'{var_type}')}}"
                )
                if var_type
                else lov_name
            )
            hash_name = self.__get_typed_hash_name(typed_lov_hash, PropertyType.lov)
            camel_prop = _to_camel_case(property_name)
            self.__update_vars.append(f"{camel_prop}={hash_name}")
            self.__set_react_attribute(camel_prop, hash_name)

        return self

    def __filter_attribute_names(self, names: t.Iterable[str]):
        return [k for k in self.__attributes if k in names or any(k.startswith(n + "[") for n in names)]

    def __get_held_name(self, key: str):
        name = self.__hashes.get(key)
        if name:
            v = self.__attributes.get(key)
            if isinstance(v, _TaipyBase):
                return name[: len(v.get_hash()) + 1]
        return name

    def __filter_attributes_hashes(self, keys: t.List[str]):
        hash_names = [k for k in self.__hashes if k in keys]
        attr_names = [k for k in keys if k not in hash_names]
        return (
            {k: v for k, v in self.__attributes.items() if k in attr_names},
            {k: self.__get_held_name(k) for k in self.__hashes if k in hash_names},
        )

    def __build_rebuild_fn(self, fn_name: str, attribute_names: t.Iterable[str]):
        rebuild = self.__attributes.get("rebuild", False)
        rebuild_hash = self.__hashes.get("rebuild")
        if rebuild_hash or _is_true(rebuild):
            attributes, hashes = self.__filter_attributes_hashes(self.__filter_attribute_names(attribute_names))
            rebuild_name = f"bool({self.__gui._get_real_var_name(rebuild_hash)[0]})" if rebuild_hash else "None"
            try:
                self.__gui._set_building(True)
                return self.__gui._evaluate_expr(
                    "{"
                    + f'{fn_name}({rebuild}, {rebuild_name}, "{quote(json.dumps(attributes))}", "{quote(json.dumps(hashes))}", {", ".join([f"{k}={v2}" for k, v2 in {v: self.__gui._get_real_var_name(t.cast(str, v))[0] for v in hashes.values()}.items()])})'  # noqa: E501
                    + "}"
                )
            finally:
                self.__gui._set_building(False)
        return None

    def _get_dataframe_attributes(self) -> "_Builder":
        date_format = _add_to_dict_and_get(self.__attributes, "date_format", "MM/dd/yyyy")
        data = self.__attributes.get("data")
        data_hash = self.__hashes.get("data", "")
        cmp_hash = ""
        if data_hash:
            cmp_idx = 1
            cmp_datas = []
            cmp_datas_hash = []
            while cmp_data := self.__hashes.get(f"data[{cmp_idx}]"):
                cmp_idx += 1
                cmp_datas.append(self.__gui._get_real_var_name(cmp_data)[0])
                cmp_datas_hash.append(cmp_data)
            if cmp_datas:
                cmp_hash = self.__gui._evaluate_expr(
                    "{"
                    + f"{self.__gui._get_call_method_name('_compare_data')}"
                    + f'({self.__gui._get_real_var_name(data_hash)[0]},{",".join(cmp_datas)})'
                    + "}"
                )
                self.__update_vars.append(f"comparedatas={','.join(cmp_datas_hash)}")
        col_types = self.__gui._get_accessor().get_col_types(data_hash, _TaipyData(data, data_hash))
        col_dict = _get_columns_dict(
            data, self.__attributes.get("columns", {}), col_types, date_format, self.__attributes.get("number_format")
        )

        rebuild_fn_hash = self.__build_rebuild_fn(
            self.__gui._get_call_method_name("_tbl_cols"), _Builder.__TABLE_COLUMNS_DEPS
        )
        if rebuild_fn_hash:
            self.__set_react_attribute("columns", rebuild_fn_hash)
        if col_dict is not None:
            _enhance_columns(self.__attributes, self.__hashes, col_dict, self.__element_name)
            self.__set_json_attribute("defaultColumns", col_dict)
        if cmp_hash:
            hash_name = self.__get_typed_hash_name(cmp_hash, PropertyType.data)
            self.__set_react_attribute(
                _to_camel_case("data"),
                _get_client_var_name(hash_name),
            )
            self.__set_update_var_name(hash_name)
            self.set_boolean_attribute("compare", True)
            self.__set_string_attribute("on_compare")

        if not isinstance(self.__attributes.get("style"), (type(None), dict, _MapDict)):
            _warn("Table: property 'style' has been renamed to 'row_class_name'.")
        if row_class_name := self.__attributes.get("row_class_name"):
            if isroutine(row_class_name):
                value = self.__hashes.get("row_class_name")
            elif isinstance(row_class_name, str):
                value = row_class_name.strip()
            else:
                value = None
            if value in col_types.keys():
                _warn(f"{self.__element_name}: row_class_name={value} must not be a column name.")
            elif value:
                self.set_attribute("rowClassName", value)
        if tooltip := self.__attributes.get("tooltip"):
            if isroutine(tooltip):
                value = self.__hashes.get("tooltip")
            elif isinstance(tooltip, str):
                value = tooltip.strip()
            else:
                value = None
            if value in col_types.keys():
                _warn(f"{self.__element_name}: tooltip={value} must not be a column name.")
            elif value:
                self.set_attribute("tooltip", value)
        return self

    def _get_chart_config(self, default_type: str, default_mode: str):
        self.__attributes["_default_type"] = default_type
        self.__attributes["_default_mode"] = default_mode
        rebuild_fn_hash = self.__build_rebuild_fn(
            self.__gui._get_call_method_name("_chart_conf"),
            _CHART_NAMES + ("_default_type", "_default_mode", "data"),
        )
        if rebuild_fn_hash:
            self.__set_react_attribute("config", rebuild_fn_hash)

        # read column definitions
        data = self.__attributes.get("data")
        data_hash = self.__hashes.get("data", "")
        col_types = self.__gui._get_accessor().get_col_types(data_hash, _TaipyData(data, data_hash))

        config = _build_chart_config(self.__gui, self.__attributes, col_types)

        self.__set_json_attribute("defaultConfig", config)
        self._set_chart_selected(max=len(config.get("traces", [])))
        self.__set_refresh_on_update()
        return self

    def _set_string_with_check(self, var_name: str, values: t.List[str], default_value: t.Optional[str] = None):
        value = self.__attributes.get(var_name, default_value)
        if value is not None:
            value = str(value).lower()
            self.__attributes[var_name] = value
            if value not in values:
                _warn(f"{self.__element_name}: {var_name}={value} should be in {values}.")
            else:
                self.__set_string_attribute(var_name, default_value)
        return self

    def __set_list_attribute(
        self,
        name: str,
        hash_name: t.Optional[str],
        val: t.Any,
        elt_type: t.Type,
        dynamic=True,
        default_val: t.Optional[t.Any] = None,
    ) -> t.List[str]:
        val = default_val if val is None else val
        if not hash_name and isinstance(val, str):
            val = [elt_type(t.strip()) for t in val.split(";")]
        if isinstance(val, list):
            if hash_name and dynamic:
                self.__set_react_attribute(name, hash_name)
                return [f"{name}={hash_name}"]
            else:
                self.__set_json_attribute(name, val)
        elif val is not None:
            _warn(f"{self.__element_name}: {name} should be a list of {elt_type}.")
        return []

    def _set_chart_selected(self, max=0):
        name = "selected"
        default_sel = self.__attributes.get(name)
        if not isinstance(default_sel, list) and name in self.__attributes:
            default_sel = []
        if max == 0:
            self.__update_vars.extend(
                self.__set_list_attribute(
                    name,
                    self.__hashes.get(name),
                    default_sel,
                    int,
                )
            )
            return
        idx = 1
        name_idx = f"{name}[{idx}]"
        sel = self.__attributes.get(name_idx)
        if not isinstance(sel, list) and name_idx in self.__attributes:
            sel = []
        while idx <= max or name_idx in self.__attributes:
            if sel is not None or default_sel is not None:
                self.__update_vars.extend(
                    self.__set_list_attribute(
                        f"{name}{idx - 1}",
                        self.__hashes.get(name_idx if sel is not None else name),
                        sel if sel is not None else default_sel,
                        int,
                    )
                )
            idx += 1
            name_idx = f"{name}[{idx}]"
            sel = self.__attributes.get(name_idx)
            if not isinstance(sel, list) and name_idx in self.__attributes:
                sel = []

    def _get_list_attribute(self, name: str, list_type: PropertyType):
        hash_name = self.__hashes.get(name)
        if hash_name is None:
            list_val = self.__attributes.get(name)
            if isinstance(list_val, str):
                list_val = list(list_val.split(";"))
            if isinstance(list_val, list):
                # TODO catch the cast exception
                if list_type.value == PropertyType.number.value:
                    list_val = [int(v) for v in list_val]
                else:
                    list_val = [int(v) for v in list_val]
            else:
                if list_val is not None:
                    _warn(f"{self.__element_name}: {name} should be a list.")
                list_val = []
            self.__set_react_attribute(_to_camel_case(name), list_val)
        else:
            self.__set_react_attribute(_to_camel_case(name), hash_name)
            self.__update_vars.append(f"{_to_camel_case(name)}={hash_name}")
        return self

    def __set_class_names(self):
        self.set_attribute("libClassName", self.__lib_name + "-" + self.__control_type.replace("_", "-"))
        return self.__set_dynamic_string_attribute("class_name", dynamic_property_name="dynamic_class_name")

    def _set_dataType(self):
        value = self.__attributes.get("value")
        return self.set_attribute("dataType", _get_data_type(value))

    def _set_file_content(self, var_name: str = "content"):
        if hash_name := self.__hashes.get(var_name):
            self.__set_update_var_name(hash_name)
        else:
            _warn(f"file_selector: {var_name} should be bound.")
        return self

    def _set_content(self, var_name: str = "content", image=True):
        content = self.__attributes.get(var_name)
        hash_name = self.__hashes.get(var_name)
        if content is None and hash_name is None:
            return self
        value = self.__gui._get_content(hash_name or var_name, content, image)
        if hash_name:
            hash_name = self.__get_typed_hash_name(hash_name, PropertyType.image if image else PropertyType.content)
        if hash_name:
            self.__set_react_attribute(
                var_name,
                _get_client_var_name(hash_name),
            )
        return self.set_attribute(_to_camel_case(f"default_{var_name}"), value)

    def __set_dynamic_string_list(self, var_name: str, default_value: t.Any):
        hash_name = self.__hashes.get(var_name)
        loi = self.__attributes.get(var_name)
        if loi is None:
            loi = default_value
        if isinstance(loi, str):
            loi = [s.strip() for s in loi.split(";") if s.strip()]
        if isinstance(loi, list):
            self.__set_json_attribute(_to_camel_case(f"default_{var_name}"), loi)
        if hash_name:
            self.__update_vars.append(f"{var_name}={hash_name}")
            self.__set_react_attribute(var_name, hash_name)
        return self

    def __set_dynamic_number_attribute(self, var_name: str, default_value: t.Any):
        hash_name = self.__hashes.get(var_name)
        numVal = self.__attributes.get(var_name)
        if numVal is None:
            numVal = default_value
        if isinstance(numVal, str):
            try:
                numVal = float(numVal)
            except Exception as e:
                _warn(f"{self.__element_name}: {var_name} cannot be transformed into a number", e)
                numVal = 0
        if isinstance(numVal, numbers.Number):
            self.__set_react_attribute(_to_camel_case(f"default_{var_name}"), numVal)
        elif numVal is not None:
            _warn(f"{self.__element_name}: {var_name} value is not valid ({numVal}).")
        if hash_name:
            hash_name = self.__get_typed_hash_name(hash_name, PropertyType.number)
            self.__update_vars.append(f"{var_name}={hash_name}")
            self.__set_react_attribute(var_name, hash_name)
        return self

    def __set_default_value(
        self,
        var_name: str,
        value: t.Optional[t.Any] = None,
        native_type: bool = False,
        var_type: t.Optional[PropertyType] = None,
    ):
        if value is None:
            value = self.__attributes.get(var_name)
        default_var_name = _to_camel_case(f"default_{var_name}")
        if isinstance(value, (datetime, date, time)):
            return self.set_attribute(default_var_name, _date_to_string(value))
        elif isinstance(value, str):
            return self.set_attribute(default_var_name, value)
        elif native_type and isinstance(value, numbers.Number):
            return self.__set_react_attribute(default_var_name, value)
        elif value is None:
            return self.__set_react_attribute(default_var_name, "null")
        elif var_type == PropertyType.lov_value:
            # Done by _get_adapter
            return self
        elif isclass(var_type) and issubclass(var_type, _TaipyBase):  # type: ignore
            return self.__set_default_value(var_name, t.cast(t.Callable, var_type)(value, "").get())
        else:
            return self.__set_json_attribute(default_var_name, value)

    def __set_update_var_name(self, hash_name: str):
        return self.set_attribute("updateVarName", hash_name)

    def set_value_and_default(
        self,
        var_name: t.Optional[str] = None,
        with_update=True,
        with_default=True,
        native_type=False,
        var_type: t.Optional[PropertyType] = None,
        default_val: t.Any = None,
    ):
        """
        TODO-undocumented
        Sets the value associated with the default property.

        Arguments:

            var_name (str): The property name (default to default property name).
            with_update (optional(bool)): Should the attribute be dynamic (default True).
            with_default (optional(bool)): Should a default attribute be set (default True).
            native_type (optional(bool)): If var_type == dynamic_number, parse the value to number.
            var_type (optional(PropertyType)): the property type (default to string).
            default_val (optional(Any)): the default value.
        """
        var_name = self.__default_property_name if var_name is None else var_name
        if var_type == PropertyType.slider_value or var_type == PropertyType.toggle_value:
            if self.__attributes.get("lov"):
                var_type = PropertyType.lov_value
                native_type = False
            elif var_type == PropertyType.toggle_value:
                self.__set_react_attribute(_to_camel_case("is_switch"), True)
                var_type = PropertyType.dynamic_boolean
                native_type = True
            else:
                var_type = (
                    PropertyType.dynamic_lo_numbers
                    if isinstance(self.__attributes.get("value"), list)
                    else PropertyType.dynamic_number
                )
                native_type = True
        if var_type == PropertyType.dynamic_boolean:
            return self.set_attributes([(var_name, var_type, bool(default_val), with_update)])
        if hash_name := self.__hashes.get(var_name):
            hash_name = self.__get_typed_hash_name(hash_name, var_type)
            self.__set_react_attribute(
                _to_camel_case(var_name),
                _get_client_var_name(hash_name),
            )
            if with_update:
                self.__set_update_var_name(hash_name)
            if with_default:
                if native_type:
                    val = self.__attributes.get(var_name)
                    if native_type and isinstance(val, str):
                        with contextlib.suppress(Exception):
                            val = float(val)
                    self.__set_default_value(var_name, val, native_type=native_type)
                else:
                    self.__set_default_value(var_name, var_type=var_type)
        else:
            if var_type == PropertyType.data and (self.__control_type != "chart" or "figure" not in self.__attributes):
                _warn(f"{self.__control_type}.{var_name} property should be bound.")
            value = self.__attributes.get(var_name)
            if value is not None:
                if native_type:
                    if isinstance(value, str):
                        with contextlib.suppress(Exception):
                            value = float(value)
                    if isinstance(value, (int, float)):
                        return self.__set_react_attribute(_to_camel_case(var_name), value)
                if isinstance(value, (datetime, date, time)):
                    value = _date_to_string(value)
                self.set_attribute(_to_camel_case(var_name), value)
        return self

    def _set_labels(self, var_name: str = "labels"):
        if value := self.__attributes.get(var_name):
            if _is_true(value):
                return self.__set_react_attribute(_to_camel_case(var_name), True)
            elif isinstance(value, (dict, _MapDict)):
                return self.set_dict_attribute(var_name)
        return self

    def _set_partial(self):
        if self.__control_type not in _Builder.__BLOCK_CONTROLS:
            return self
        if partial := self.__attributes.get("partial"):
            if self.__attributes.get("page"):
                _warn(f"{self.__element_name} control: page and partial should not be both defined.")
            if isinstance(partial, Partial):
                self.__attributes["page"] = partial._route
                self.__set_react_attribute("partial", partial._route)
                self.__set_react_attribute("defaultPartial", True)
        return self

    def _set_propagate(self):
        val = self.__get_boolean_attribute("propagate", t.cast(bool, self.__gui._config.config.get("propagate")))
        return self if val else self.set_boolean_attribute("propagate", False)

    def __set_refresh_on_update(self):
        if self.__update_vars:
            self.set_attribute("updateVars", ";".join(self.__update_vars))
        return self

    def _set_table_pagesize_options(self, default_size=None):
        if default_size is None:
            default_size = [50, 100, 500]
        page_size_options = self.__attributes.get("page_size_options", default_size)
        if isinstance(page_size_options, str):
            try:
                page_size_options = [int(s.strip()) for s in page_size_options.split(";")]
            except Exception as e:
                _warn(f"{self.__element_name}: page_size_options value is invalid ({page_size_options})", e)
        if isinstance(page_size_options, list):
            self.__set_json_attribute("pageSizeOptions", page_size_options)
        else:
            _warn(f"{self.__element_name}: page_size_options should be a list.")
        return self

    def _set_input_type(self, type_name: str, allow_password=False):
        if allow_password and self.__get_boolean_attribute("password", False):
            return self.set_attribute("type", "password")
        return self.set_attribute("type", self.__attributes.get("type", type_name))

    def _set_kind(self):
        if self.__attributes.get("theme", False):
            self.set_attribute("mode", "theme")
        return self

    def __get_typed_hash_name(self, hash_name: str, var_type: t.Optional[PropertyType]) -> str:
        if taipy_type := _get_taipy_type(var_type):
            expr = self.__gui._get_expr_from_hash(hash_name)
            hash_name = self.__gui._evaluate_bind_holder(t.cast(t.Type[_TaipyBase], taipy_type), expr)
        return hash_name

    def __set_dynamic_bool_attribute(self, name: str, def_val: t.Any, with_update: bool, update_main=True):
        hash_name = self.__hashes.get(name)
        val = self.__get_boolean_attribute(name, def_val)
        default_name = f"default_{name}" if hash_name is not None else name
        if val != def_val:
            self.set_boolean_attribute(default_name, val)
        if hash_name is not None:
            hash_name = self.__get_typed_hash_name(hash_name, PropertyType.dynamic_boolean)
            self.__set_react_attribute(_to_camel_case(name), _get_client_var_name(hash_name))
            if with_update:
                if update_main:
                    self.__set_update_var_name(hash_name)
                else:
                    self.__update_vars.append(f"{_to_camel_case(name)}={hash_name}")

    def __set_dynamic_property_without_default(
        self, name: str, property_type: PropertyType, optional: t.Optional[bool] = False
    ):
        hash_name = self.__hashes.get(name)
        if hash_name is None:
            if not optional:
                _warn(f"{self.__element_name}.{name} should be bound.")
        else:
            hash_name = self.__get_typed_hash_name(hash_name, property_type)
            self.__update_vars.append(f"{_to_camel_case(name)}={hash_name}")
            self.__set_react_attribute(_to_camel_case(name), _get_client_var_name(hash_name))
        return self

    def __set_html_content(self, name: str, property_name: str, property_type: PropertyType):
        hash_name = self.__hashes.get(name)
        if not hash_name:
            return self
        front_var = self.__get_typed_hash_name(hash_name, property_type)
        self.set_attribute(
            _to_camel_case(f"default_{property_name}"),
            self.__gui._get_user_content_url(
                None,
                {
                    "variable_name": front_var,
                    self.__gui._HTML_CONTENT_KEY: str(_time.time()),
                },
            ),
        )
        return self.__set_react_attribute(_to_camel_case(property_name), _get_client_var_name(front_var))

    def set_attributes(self, attributes: t.List[tuple]):  # noqa: C901
        """
        TODO-undocumented
        Sets the attributes from the property with type and default value.

        Arguments:

            attributes (list(tuple)): The list of attributes as (property name, property type, default value).
        """
        attributes.append(("id",))  # Every element should have an id attribute
        for attr in attributes:
            if not isinstance(attr, tuple):
                attr = (attr,)
            var_type = _get_tuple_val(attr, 1, PropertyType.string)
            if var_type == PropertyType.to_json:
                var_type = _TaipyToJson
            if var_type == PropertyType.boolean:
                def_val = _get_tuple_val(attr, 2, False)
                if isinstance(def_val, bool) or self.__attributes.get(attr[0], None) is not None:
                    val = self.__get_boolean_attribute(attr[0], def_val)
                    if val != def_val:
                        self.set_boolean_attribute(attr[0], val)
            elif var_type == PropertyType.dynamic_boolean:
                self.__set_dynamic_bool_attribute(
                    attr[0],
                    _get_tuple_val(attr, 2, False),
                    _get_tuple_val(attr, 3, False),
                    _get_tuple_val(attr, 4, True),
                )
            elif var_type == PropertyType.number:
                self.set_number_attribute(attr[0], _get_tuple_val(attr, 2, None))
            elif var_type == PropertyType.dynamic_number:
                self.__set_dynamic_number_attribute(attr[0], _get_tuple_val(attr, 2, None))
            elif var_type == PropertyType.string:
                self.__set_string_attribute(attr[0], _get_tuple_val(attr, 2, None), _get_tuple_val(attr, 3, True))
            elif var_type == PropertyType.dynamic_string:
                self.__set_dynamic_string_attribute(
                    attr[0], _get_tuple_val(attr, 2, None), _get_tuple_val(attr, 3, False)
                )
            elif var_type == PropertyType.string_list:
                self.__update_vars.extend(
                    self.__set_list_attribute(
                        attr[0],
                        self.__hashes.get(attr[0]),
                        self.__attributes.get(attr[0]),
                        str,
                        False,
                        _get_tuple_val(attr, 2, None),
                    )
                )
            elif var_type == PropertyType.function:
                self.__set_function_attribute(attr[0], _get_tuple_val(attr, 2, None), _get_tuple_val(attr, 3, True))
            elif var_type == PropertyType.react:
                prop_name = _to_camel_case(attr[0])
                if hash_name := self.__hashes.get(attr[0]):
                    self.__update_vars.append(f"{prop_name}={hash_name}")
                    self.__set_react_attribute(prop_name, hash_name)
                else:
                    self.__set_react_attribute(prop_name, self.__attributes.get(attr[0], _get_tuple_val(attr, 2, None)))
            elif var_type == PropertyType.broadcast:
                self.__set_react_attribute(
                    _to_camel_case(attr[0]), _get_broadcast_var_name(_get_tuple_val(attr, 2, None))
                )
            elif var_type == PropertyType.string_or_number:
                self.__set_string_or_number_attribute(attr[0], _get_tuple_val(attr, 2, None))
            elif var_type == PropertyType.dict:
                self.set_dict_attribute(attr[0], _get_tuple_val(attr, 2, None))
            elif var_type == PropertyType.dynamic_dict:
                self.set_dynamic_dict_attribute(attr[0], _get_tuple_val(attr, 2, None))
            elif var_type == PropertyType.dynamic_list:
                self.__set_dynamic_string_list(attr[0], _get_tuple_val(attr, 2, None))
            elif var_type == PropertyType.boolean_or_list:
                if _is_boolean(self.__attributes.get(attr[0])):
                    self.__set_dynamic_bool_attribute(attr[0], _get_tuple_val(attr, 2, False), True, update_main=False)
                else:
                    self.__set_dynamic_string_list(attr[0], _get_tuple_val(attr, 2, None))
            elif var_type == PropertyType.dynamic_date:
                self.__set_dynamic_date_attribute(attr[0], _get_tuple_val(attr, 2, None))
            elif var_type == PropertyType.data:
                self.__set_dynamic_property_without_default(attr[0], t.cast(PropertyType, var_type))
            elif (
                var_type == PropertyType.lov
                or var_type == PropertyType.single_lov
                or var_type == PropertyType.lov_no_default
            ):
                self._get_lov_adapter(
                    attr[0],
                    multi_selection=var_type != PropertyType.single_lov,
                    with_default=var_type != PropertyType.lov_no_default,
                )
            elif var_type == PropertyType.lov_value:
                self.__set_dynamic_property_without_default(
                    attr[0], t.cast(PropertyType, var_type), _get_tuple_val(attr, 2, None) == "optional"
                )
            elif var_type == PropertyType.toHtmlContent:
                self.__set_html_content(attr[0], "page", t.cast(PropertyType, var_type))
            elif isclass(var_type) and issubclass(var_type, _TaipyBase):
                prop_name = _to_camel_case(attr[0])
                if hash_name := self.__hashes.get(attr[0]):
                    expr = self.__gui._get_expr_from_hash(hash_name)
                    hash_name = self.__gui._evaluate_bind_holder(var_type, expr)
                    self.__update_vars.append(f"{prop_name}={hash_name}")
                    self.__set_react_attribute(prop_name, hash_name)
                else:
                    val = self.__attributes.get(attr[0])
                    self.set_attribute(
                        prop_name, var_type(_get_tuple_val(attr, 2, None) if val is None else val, "").get()
                    )

        self.__set_refresh_on_update()
        return self

    def set_attribute(self, name: str, value: t.Any):
        """
        TODO-undocumented
        Sets an attribute.

        Arguments:

            name (str): The name of the attribute.
            value (Any): The value of the attribute (must be json serializable).
        """
        if value is not None:
            self.el.set(name, value)
        return self

    def get_element(self):
        """
        TODO-undocumented
        Returns the xml.etree.ElementTree.Element
        """
        return self.el

    def _build_to_string(self):
        el_str = str(etree.tostring(self.el, encoding="utf8").decode("utf8"))
        el_str = el_str.replace("<?xml version='1.0' encoding='utf8'?>\n", "")
        el_str = el_str.replace("/>", ">")
        return el_str, self.__element_name
