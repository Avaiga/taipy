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

import contextlib
import json
import numbers
import re
import typing as t
import warnings
import xml.etree.ElementTree as etree
from datetime import date, datetime, time
from inspect import isclass

from ..partial import Partial
from ..types import PropertyType, _get_taipy_type
from ..utils import (
    _date_to_ISO,
    _get_client_var_name,
    _get_data_type,
    _get_expr_var_name,
    _getscopeattr,
    _getscopeattr_drill,
    _is_boolean,
    _is_boolean_true,
    _MapDict,
)
from ..utils.types import _TaipyData
from .json import _TaipyJsonEncoder
from .utils import (
    _add_to_dict_and_get,
    _get_col_from_indexed,
    _get_columns_dict,
    _get_idx_from_col,
    _get_tuple_val,
    _to_camel_case,
)

if t.TYPE_CHECKING:
    from ..gui import Gui


class _Builder:
    """
    Constructs an XML node that can be rendered as a React node.

    This class can only be instantiated internally by Taipy.
    """

    __keys: t.Dict[str, int] = {}

    __ONE_COLUMN_CHART = ["pie"]

    __BLOCK_CONTROLS = ["dialog", "expandable", "pane", "part"]

    def __init__(
        self,
        gui: "Gui",
        control_type: str,
        element_name: str,
        attributes: t.Union[t.Dict[str, t.Any], None],
        hash_names: t.Dict[str, str] = {},
        default_value="<Empty>",
        lib_name: str = "taipy",
    ):
        from ..gui import Gui
        from .factory import _Factory

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

        # Bind properties dictionary to attributes if condition is matched (will leave the binding for function at the builder )
        if "properties" in self.__attributes:
            (prop_dict, prop_hash) = _Builder.__parse_attribute_value(gui, self.__attributes["properties"])
            if prop_hash is None:
                prop_hash = prop_dict
                prop_hash = self.__gui._bind_var(prop_hash)
                if hasattr(self.__gui._bindings(), prop_hash):
                    prop_dict = _getscopeattr(self.__gui, prop_hash)
            if isinstance(prop_dict, _MapDict):
                # Iterate through prop_dict and append to self.attributes
                for k, v in prop_dict.items():
                    (val, key_hash) = _Builder.__parse_attribute_value(gui, v)
                    self.__attributes[k] = f"{{{prop_hash}['{k}']}}" if key_hash is None else v
            else:
                warnings.warn(f"{self.__control_type}.properties ({prop_hash}) must be a dict.")

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
                if callable(func):
                    return (func, hash_value)
                return (_getscopeattr_drill(gui, hash_value), hash_value)
            except AttributeError:
                warnings.warn(f"Expression '{value}' cannot be evaluated")
        return (value, None)

    @staticmethod
    def _get_variable_hash_names(
        gui: "Gui", attributes: t.Dict[str, t.Any], hash_names: t.Dict[str, str] = {}
    ) -> t.Dict[str, str]:
        hashes = {}
        # Bind potential function and expressions in self.attributes
        for k, v in attributes.items():
            val = v
            hashname = hash_names.get(k)
            if hashname is None:
                if callable(v):
                    if v.__name__ == "<lambda>":
                        hashname = _get_expr_var_name(v.__code__)
                        gui._bind_var_val(hashname, v)
                    else:
                        hashname = _get_expr_var_name(v.__name__)
                elif isinstance(v, str):
                    # need to unescape the double quotes that were escaped during preprocessing
                    (val, hashname) = _Builder.__parse_attribute_value(gui, v.replace('\\"', '"'))

                if val is not None or hashname:
                    attributes[k] = val
                if hashname:
                    hashes[k] = hashname
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

    def __get_list_of_(self, name: str):
        lof = self.__attributes.get(name)
        if isinstance(lof, str):
            lof = list(lof.split(";"))
        return lof

    def get_name_indexed_property(self, name: str) -> t.Dict[str, t.Any]:
        """
        TODO
        Returns all properties defined as <property name>[<named index>] as a dict.

        Arguments:

            name (str): The property name.
        """
        ret = {}
        index_re = re.compile(name + r"\[(.*)\]$")
        for key in self.__attributes.keys():
            if m := index_re.match(key):
                ret[m.group(1)] = self.__attributes.get(key)
        return ret

    def __get_multiple_indexed_attributes(
        self, names: t.Tuple[str], index: t.Optional[int] = None
    ) -> t.List[t.Optional[str]]:
        names = names if index is None else [f"{n}[{index}]" for n in names]  # type: ignore
        return [self.__attributes.get(name) for name in names]

    def __get_boolean_attribute(self, name: str, default_value=False):
        boolattr = self.__attributes.get(name, default_value)
        return _is_boolean_true(boolattr) if isinstance(boolattr, str) else bool(boolattr)

    def set_boolean_attribute(self, name: str, value: bool):
        """
        TODO
        Defines a React Boolean attribute (attr={true|false}).

        Arguments:
            name (str): The property name.
            value (bool): the boolean value.
        """
        return self.__set_react_attribute(_to_camel_case(name), value)

    def set_dict_attribute(self, name: str):
        """
        TODO
        Defines a React attribute as a stringified json dict.
        The original property can be a dict or a string formed as <key 1>:<value 1>;<key 2>:<value 2>.

        Arguments:
            name (str): The property name.
        """
        if dict_attr := self.__attributes.get(name):
            if isinstance(dict_attr, str):
                vals = [x.strip().split(":") for x in dict_attr.split(";")]
                dict_attr = {val[0].strip(): val[1].strip() for val in vals if len(val) > 1}
            if isinstance(dict_attr, (dict, _MapDict)):
                self.__set_json_attribute(_to_camel_case(name), dict_attr)
            else:
                warnings.warn(f"{self.__element_name} {name} should be a dict\n'{str(dict_attr)}'")
        return self

    def __set_json_attribute(self, name, value):
        return self.set_attribute(name, json.dumps(value, cls=_TaipyJsonEncoder))

    def __set_list_of_(self, name: str):
        lof = self.__get_list_of_(name)
        if not isinstance(lof, (list, tuple)):
            if lof is not None:
                warnings.warn(f"{self.__element_name} {name} should be a list")
            return self
        return self.__set_json_attribute(_to_camel_case(name), lof)

    def set_number_attribute(self, name: str, default_value: t.Optional[str] = None, optional: t.Optional[bool] = True):
        """
        TODO
        Defines a React number attribute (attr={<number>}).

        Arguments:

            name (str): The property name.
            default_value (optional(str)): the default value as a string.
            optional (bool): Default to True, the property is required if False.
        """
        value = self.__attributes.get(name, default_value)
        if value is None:
            if not optional:
                warnings.warn(f"Property {name} is required for control {self.__control_type}")
            return self
        try:
            val = float(value)
        except ValueError:
            raise ValueError(f"Property {name} expects a number for control {self.__control_type}")
        return self.__set_react_attribute(_to_camel_case(name), val)

    def __set_string_attribute(
        self, name: str, default_value: t.Optional[str] = None, optional: t.Optional[bool] = True
    ):
        strattr = self.__attributes.get(name, default_value)
        if strattr is None:
            if not optional:
                warnings.warn(f"Property {name} is required for control {self.__control_type}")
            return self
        return self.set_attribute(_to_camel_case(name), str(strattr))

    def __set_dynamic_string_attribute(
        self, name: str, default_value: t.Optional[str] = None, with_update: t.Optional[bool] = False
    ):
        hash_name = self.__hashes.get(name)
        str_val = self.__attributes.get(name, default_value)
        if str_val is not None:
            self.set_attribute(_to_camel_case(f"default_{name}"), str(str_val))
        if hash_name:
            if with_update:
                self.__update_vars.append(f"{name}={hash_name}")
            self.__set_react_attribute(name, hash_name)
        return self

    def __set_function_attribute(
        self, name: str, default_value: t.Optional[str] = None, optional: t.Optional[bool] = True
    ):
        strattr = self.__attributes.get(name, default_value)
        if strattr is None:
            if not optional:
                warnings.warn(f"Property {name} is required for control {self.__control_type}")
            return self
        elif callable(strattr):
            strattr = self.__hashes.get(name)
            if strattr is None:
                return self
        elif strattr:
            strattr = str(strattr)
            func = self.__gui._get_user_function(strattr)
            if func == strattr:
                warnings.warn(f" {self.__control_type}.{name}: {strattr} is not a function")
        return self.set_attribute(_to_camel_case(name), strattr) if strattr else self

    def __set_decimator_attribute(self, attr_name: str):
        strattr = self.__attributes.get(attr_name)
        cls = self.__gui._get_user_instance(class_name=str(strattr), class_type=PropertyType.decimator.value)
        if isinstance(cls, PropertyType.decimator.value):
            self.__set_string_or_number_attribute(attr_name, strattr)

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

    def _get_adapter(self, var_name: str, property_name: t.Optional[str] = None, multi_selection=True):  # noqa: C901
        property_name = var_name if property_name is None else property_name
        lov = self.__get_list_of_(var_name)
        if isinstance(lov, list):
            adapter = self.__attributes.get("adapter")
            if adapter and isinstance(adapter, str):
                adapter = self.__gui._get_user_function(adapter)
            if adapter and not callable(adapter):
                warnings.warn("'adapter' property value is invalid")
                adapter = None
            var_type = self.__attributes.get("type")
            if isclass(var_type):
                var_type = var_type.__name__  # type: ignore
            if not isinstance(var_type, str):
                elt = None
                if len(lov) == 0:
                    value = self.__attributes.get("value")
                    if isinstance(value, list):
                        if len(value) > 0:
                            elt = value[0]
                    else:
                        elt = value
                else:
                    elt = lov[0]
                var_type = self.__gui._get_unique_type_adapter(type(elt).__name__)
            if adapter is None:
                adapter = self.__gui._get_adapter_for_type(var_type)
            if lov_name := self.__hashes.get(var_name):
                if adapter is None:
                    adapter = self.__gui._get_adapter_for_type(lov_name)
                else:
                    self.__gui._add_type_for_var(lov_name, var_type)
            if value_name := self.__hashes.get("value"):
                if adapter is None:
                    adapter = self.__gui._get_adapter_for_type(value_name)
                else:
                    self.__gui._add_type_for_var(value_name, var_type)
            if adapter is not None:
                self.__gui._add_adapter_for_type(var_type, adapter)  # type: ignore

            ret_list = []
            if len(lov) > 0:
                for elt in lov:
                    ret = self.__gui._run_adapter(
                        t.cast(t.Callable, adapter), elt, adapter.__name__ if callable(adapter) else "adapter"
                    )  # type: ignore
                    if ret is not None:
                        ret_list.append(ret)
            self.__attributes[f"default_{property_name}"] = ret_list

            ret_list = []
            value = self.__attributes.get("value")
            val_list = value if isinstance(value, list) else [value]
            for val in val_list:
                ret = self.__gui._run_adapter(
                    t.cast(t.Callable, adapter), val, adapter.__name__ if callable(adapter) else "adapter", id_only=True
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
        return self

    def __update_col_desc_from_indexed(self, columns: t.Dict[str, t.Any], name: str):
        col_value = self.get_name_indexed_property(name)
        for k, v in col_value.items():
            if col_desc := next((x for x in columns.values() if x["dfid"] == k), None):
                if col_desc.get(_to_camel_case(name)) is None:
                    col_desc[_to_camel_case(name)] = str(v)
            else:
                warnings.warn(f"{self.__element_name} {name}[{k}] is not in the list of displayed columns")

    def _get_dataframe_attributes(self, date_format="MM/dd/yyyy", number_format=None):  # noqa: C901
        data = self.__attributes.get("data")
        data_hash = self.__hashes.get("data", "")
        col_types = self.__gui._accessors._get_col_types(data_hash, _TaipyData(data, data_hash))
        columns = _get_columns_dict(
            data,
            _add_to_dict_and_get(self.__attributes, "columns", {}),
            col_types,
            _add_to_dict_and_get(self.__attributes, "date_format", date_format),
            _add_to_dict_and_get(self.__attributes, "number_format", number_format),
        )
        if columns is not None:
            self.__update_col_desc_from_indexed(columns, "nan_value")
            self.__update_col_desc_from_indexed(columns, "width")
            filters = self.get_name_indexed_property("filter")
            for k, v in filters.items():
                if _is_boolean_true(v):
                    if col_desc := next((x for x in columns.values() if x["dfid"] == k), None):
                        col_desc["filter"] = True
                    else:
                        warnings.warn(f"{self.__element_name} filter[{k}] is not in the list of displayed columns")
            editables = self.get_name_indexed_property("editable")
            for k, v in editables.items():
                if _is_boolean(v):
                    if col_desc := next((x for x in columns.values() if x["dfid"] == k), None):
                        col_desc["notEditable"] = not _is_boolean_true(v)
                    else:
                        warnings.warn(f"{self.__element_name} editable[{k}] is not in the list of displayed columns")
            group_by = self.get_name_indexed_property("group_by")
            for k, v in group_by.items():
                if _is_boolean_true(v):
                    if col_desc := next((x for x in columns.values() if x["dfid"] == k), None):
                        col_desc["groupBy"] = True
                    else:
                        warnings.warn(f"{self.__element_name} group_by[{k}] is not in the list of displayed columns")
            apply = self.get_name_indexed_property("apply")
            for k, v in apply.items():  # pragma: no cover
                if col_desc := next((x for x in columns.values() if x["dfid"] == k), None):
                    if callable(v):
                        value = self.__hashes.get(f"apply[{k}]")
                    elif isinstance(v, str):
                        value = v.strip()
                    else:
                        warnings.warn(f"{self.__element_name} apply[{k}] should be a user or predefined function")
                        value = None
                    if value:
                        col_desc["apply"] = value
                else:
                    warnings.warn(f"{self.__element_name} apply[{k}] is not in the list of displayed columns")
            if line_style := self.__attributes.get("style"):
                if callable(line_style):
                    value = self.__hashes.get("style")
                elif isinstance(line_style, str):
                    value = line_style.strip()
                else:
                    value = None
                if value in col_types.keys():
                    warnings.warn(f"{self.__element_name} style={value} cannot be a column's name")
                elif value:
                    self.set_attribute("lineStyle", value)
            styles = self.get_name_indexed_property("style")
            for k, v in styles.items():  # pragma: no cover
                if col_desc := next((x for x in columns.values() if x["dfid"] == k), None):
                    if callable(v):
                        value = self.__hashes.get(f"style[{k}]")
                    elif isinstance(v, str):
                        value = v.strip()
                    else:
                        value = None
                    if value in col_types.keys():
                        warnings.warn(f"{self.__element_name} style[{k}]={value} cannot be a column's name")
                    elif value:
                        col_desc["style"] = value
                else:
                    warnings.warn(f"{self.__element_name} style[{k}] is not in the list of displayed columns")
            self.__attributes["columns"] = columns
            self.__set_json_attribute("columns", columns)
        return self

    def __check_dict(self, values: t.List[t.Any], indexes: t.Tuple[int], names: t.Tuple[str]) -> None:
        for index in indexes:
            if values[index] is not None and not isinstance(values[index], (dict, _MapDict)):
                warnings.warn(f"{self.__element_name} {names[index]} should be a dict")
                values[index] = None

    def _get_chart_config(self, default_type="scatter", default_mode="lines+markers"):  # noqa: C901
        names = (
            "x",  # 0
            "y",
            "z",  # 2
            "label",
            "text",  # 4
            "mode",
            "type",  # 6
            "color",
            "xaxis",  # 8
            "yaxis",
            "selected_color",  # 10
            "marker",
            "selected_marker",  # 12
            "orientation",
            "name",  # 14
            "line",
            "text_anchor",  # 16
            "options",
            "lon",  # 18
            "lat",
            "base",  # 20
        )
        trace = self.__get_multiple_indexed_attributes(names)
        if not trace[0] and trace[18]:
            trace[0] = trace[18]  # substitute Lon to x
        if not trace[1] and trace[19]:
            trace[1] = trace[19]  # substitute Lat to y
        if not trace[5]:
            # mode
            trace[5] = default_mode
        trace[6] = str(trace[6]).strip().lower() if trace[6] else default_type
        if not trace[8]:
            # xaxis
            trace[8] = "x"
        if not trace[9]:
            # yaxis
            trace[9] = "y"
        self.__check_dict(trace, (11, 12, 17), names)
        traces = []
        idx = 1
        indexed_trace = self.__get_multiple_indexed_attributes(names, idx)
        if len([x for x in indexed_trace if x]):
            while len([x for x in indexed_trace if x]):
                if not indexed_trace[0] and indexed_trace[18]:
                    indexed_trace[0] = indexed_trace[18]  # substitute Lon to x
                if not indexed_trace[1] and indexed_trace[19]:
                    indexed_trace[1] = indexed_trace[19]  # substitute Lat to y
                self.__check_dict(indexed_trace, (11, 12, 17), names)
                traces.append([x or trace[i] for i, x in enumerate(indexed_trace)])
                idx += 1
                indexed_trace = self.__get_multiple_indexed_attributes(names, idx)
        else:
            traces.append(trace)

        # read column definitions
        data = self.__attributes.get("data")
        data_hash = self.__hashes.get("data", "")
        col_types = self.__gui._accessors._get_col_types(data_hash, _TaipyData(data, data_hash))

        # add trace for non used indexed columns
        max_idx = max(_get_idx_from_col(c) for c in col_types.keys())
        traces.extend([x if i > 4 else None for i, x in enumerate(traces[0])] for _ in range(len(traces), max_idx + 1))

        # configure columns
        columns = set()
        for trace in traces:
            columns.update([t for t in trace[:5] if t])
            if trace[20]:
                columns.add(trace[20])
        # add optionnal column if any
        markers = [t[11] or ({"color": t[7]} if t[7] else None) for t in traces]
        opt_cols = set()
        for m in markers:
            if isinstance(m, (dict, _MapDict)):
                color = m.get("color")
                if isinstance(color, str) and color not in columns:
                    opt_cols.add(color)
                size = m.get("size")
                if isinstance(size, str) and size not in columns:
                    opt_cols.add(size)

        # Validate the column names
        columns = _get_columns_dict(data, list(columns), col_types, opt_columns=opt_cols)
        # set default columns if not defined
        icols = [[c for c in [_get_col_from_indexed(c, i) for c in columns.keys()] if c] for i in range(len(traces))]

        for i, tr in enumerate(traces):
            if not tr[0] or tr[6] in _Builder.__ONE_COLUMN_CHART or not tr[1]:
                traces[i] = tuple(
                    v or (icols[i].pop(0) if j < 3 and j < len(icols[i]) else v) for j, v in enumerate(tr)
                )

        if columns is not None:
            self.__attributes["columns"] = columns
            reverse_cols = {cd["dfid"]: c for c, cd in columns.items()}

            ret_dict = {
                "columns": columns,
                "labels": [reverse_cols.get(t[3], (t[3] or "")) for t in traces],
                "texts": [reverse_cols.get(t[4], (t[4] or None)) for t in traces],
                "modes": [t[5] for t in traces],
                "types": [t[6] for t in traces],
                "xaxis": [t[8] for t in traces],
                "yaxis": [t[9] for t in traces],
                "markers": markers,
                "selectedMarkers": [t[12] or ({"color": t[10]} if t[10] else None) for t in traces],
                "traces": [[reverse_cols.get(c, c) for c in [t[0], t[1], t[2]]] for t in traces],
                "orientations": [t[13] for t in traces],
                "names": [t[14] for t in traces],
                "lines": [t[15] if isinstance(t[15], dict) else {"dash": t[15]} for t in traces],
                "textAnchors": [t[16] for t in traces],
                "options": [t[17] for t in traces],
                "bases": [reverse_cols.get(t[20], (t[20] or "")) for t in traces],
            }

            self.__set_json_attribute("config", ret_dict)
            self._set_chart_selected(max=len(traces))
            self.__set_refresh_on_update()
        return self

    def _set_chart_layout(self):
        if layout := self.__attributes.get("layout"):
            if isinstance(layout, (dict, _MapDict)):
                self.__set_json_attribute("layout", layout)
            else:
                warnings.warn(f"Chart control: layout attribute should be a dict\n'{str(layout)}'")

    def _set_string_with_check(self, var_name: str, values: t.List[str], default_value: t.Optional[str] = None):
        value = self.__attributes.get(var_name, default_value)
        if value is not None:
            value = str(value).lower()
            self.__attributes[var_name] = value
            if value not in values:
                warnings.warn(f"{self.__element_name} {var_name}={value} should be in {values}")
            else:
                self.__set_string_attribute(var_name, default_value)
        return self

    def __set_list_attribute(
        self, name: str, hash_name: t.Optional[str], val: t.Any, elt_type: t.Type, dynamic=True
    ) -> t.List[str]:
        if not hash_name and isinstance(val, str):
            val = [elt_type(t.strip()) for t in val.split(";")]
        if isinstance(val, list):
            if hash_name and dynamic:
                self.__set_react_attribute(name, hash_name)
                return [f"{name}={hash_name}"]
            else:
                self.__set_json_attribute(name, val)
        elif val is not None:
            warnings.warn(f"{self.__element_name} {name} should be a list of {elt_type}")
        return []

    def _set_chart_selected(self, max=0):
        name = "selected"
        default_sel = self.__attributes.get(name)
        idx = 1
        name_idx = f"{name}[{idx}]"
        sel = self.__attributes.get(name_idx)
        while idx <= max:
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

    def _get_list_attribute(self, name: str, list_type: PropertyType):
        varname = self.__hashes.get(name)
        if varname is None:
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
                    warnings.warn(f"{self.__element_name} {name} should be a list")
                list_val = []
            self.__set_react_attribute(_to_camel_case(name), list_val)
        else:
            self.__set_react_attribute(_to_camel_case(name), varname)
        return self

    def __set_class_names(self):
        classes = [self.__lib_name + "-" + self.__control_type.replace("_", "-")]
        if cl := self.__attributes.get("class_name"):
            classes.append(str(cl))

        return self.set_attribute("className", " ".join(classes))

    def _set_dataType(self):
        value = self.__attributes.get("value")
        return self.set_attribute("dataType", _get_data_type(value))

    def _set_file_content(self, var_name: str = "content"):
        if hash_name := self.__hashes.get(var_name):
            self.__set_update_var_name(hash_name)
        else:
            warnings.warn("{self.element_name} {var_name} should be bound")
        return self

    def _set_content(self, var_name: str = "content", image=True):
        content = self.__attributes.get(var_name)
        hash_name = self.__hashes.get(var_name)
        if content is None and hash_name is None:
            return self
        if hash_name:
            hash_name = self.__get_typed_hash_name(hash_name, PropertyType.image if image else PropertyType.content)
        value = self.__gui._get_content(hash_name or var_name, content, image)
        if hash_name:
            self.__set_react_attribute(
                var_name,
                _get_client_var_name(hash_name),
            )
        return self.set_attribute(_to_camel_case(f"default_{var_name}"), value)

    def _set_lov(self, var_name="lov", property_name: t.Optional[str] = None):
        property_name = var_name if property_name is None else property_name
        self.__set_list_of_(f"default_{property_name}")
        if hash_name := self.__hashes.get(var_name):
            hash_name = self.__get_typed_hash_name(hash_name, PropertyType.lov)
            self.__update_vars.append(f"{property_name}={hash_name}")
            self.__set_react_attribute(property_name, hash_name)
        return self

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
                warnings.warn(f"{self.__element_name} {var_name} cannot be transformed into a number\n{e}")
                numVal = 0
        if isinstance(numVal, numbers.Number):
            self.__set_react_attribute(_to_camel_case(f"default_{var_name}"), numVal)
        elif numVal is not None:
            warnings.warn(f"{self.__element_name} {var_name} value is not not valid {numVal}")
        if hash_name:
            hash_name = self.__get_typed_hash_name(hash_name, PropertyType.number)
            self.__update_vars.append(f"{var_name}={hash_name}")
            self.__set_react_attribute(var_name, hash_name)
        return self

    def __set_default_value(self, var_name: str, value: t.Optional[t.Any] = None, native_type: bool = False):
        if value is None:
            value = self.__attributes.get(var_name)
        default_var_name = _to_camel_case(f"default_{var_name}")
        if isinstance(value, (datetime, date, time)):
            self.set_attribute(default_var_name, _date_to_ISO(value))
        elif isinstance(value, str):
            self.set_attribute(default_var_name, value)
        elif native_type and isinstance(value, numbers.Number):
            self.__set_react_attribute(default_var_name, value)
        elif value is None:
            self.__set_react_attribute(default_var_name, "null")
        else:
            self.__set_json_attribute(default_var_name, value)
        return self

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
        TODO
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
        if var_type == PropertyType.number_or_lov_value:
            var_type = PropertyType.lov_value if self.__attributes.get("lov") else PropertyType.dynamic_number
            native_type = native_type if var_type == PropertyType.dynamic_number else False
        if var_type == PropertyType.dynamic_boolean:
            return self.set_attributes([(var_name, var_type, bool(default_val), with_update)])
        if hash_name := self.__hashes.get(var_name):
            hash_name = self.__get_typed_hash_name(hash_name, var_type)
            self.__set_react_attribute(
                var_name,
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
                    self.__set_default_value(var_name)
        else:
            value = self.__attributes.get(var_name)
            if value is not None:
                if native_type:
                    if isinstance(value, str):
                        with contextlib.suppress(Exception):
                            value = float(value)
                    if isinstance(value, (int, float)):
                        return self.__set_react_attribute(var_name, value)
                self.set_attribute(var_name, value)
        return self

    def _set_labels(self, var_name: str = "labels"):
        if value := self.__attributes.get(var_name):
            if _is_boolean_true(value):
                return self.__set_react_attribute(_to_camel_case(var_name), True)
            elif isinstance(value, (dict, _MapDict)):
                return self.set_dict_attribute(var_name)
        return self

    def _set_partial(self):
        if self.__control_type not in _Builder.__BLOCK_CONTROLS:
            return self
        if partial := self.__attributes.get("partial"):
            if self.__attributes.get("page"):
                warnings.warn(
                    f"{self.__element_name} control: page and partial should not be defined at the same time."
                )
            if isinstance(partial, Partial):
                self.__attributes["page"] = partial._route
                self.__set_react_attribute("partial", partial._route)
        return self

    def _set_propagate(self):
        val = self.__get_boolean_attribute("propagate", self.__gui._config.config.get("propagate"))
        return self if val else self.set_boolean_attribute("propagate", False)

    def __set_refresh_on_update(self):
        if self.__update_vars:
            self.set_attribute("updateVars", ";".join(self.__update_vars))
        return self

    def _set_table_pagesize_options(self, default_size=[50, 100, 500]):
        page_size_options = self.__attributes.get("page_size_options", default_size)
        if isinstance(page_size_options, str):
            try:
                page_size_options = [int(s.strip()) for s in page_size_options.split(";")]
            except Exception as e:
                warnings.warn(f"{self.__element_name} page_size_options: invalid value {page_size_options}\n{e}")
        if isinstance(page_size_options, list):
            self.__set_json_attribute("pageSizeOptions", page_size_options)
        else:
            warnings.warn(f"{self.__element_name} page_size_options should be a list")
        return self

    def _set_input_type(self, type_name: str, allow_password=False):
        if allow_password and self.__get_boolean_attribute("password", False):
            return self.set_attribute("type", "password")
        return self.set_attribute("type", type_name)

    def _set_kind(self):
        if self.__attributes.get("theme", False):
            self.set_attribute("kind", "theme")
        return self

    def __get_typed_hash_name(self, hash_name: str, var_type: t.Optional[PropertyType]) -> str:
        if taipy_type := _get_taipy_type(var_type):
            expr = self.__gui._get_expr_from_hash(hash_name)
            hash_name = self.__gui._evaluate_bind_holder(taipy_type, expr)
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

    def __set_dynamic_property_without_default(self, name: str, property_type: PropertyType):
        hash_name = self.__hashes.get(name)
        if hash_name is None:
            warnings.warn(f"{self.__element_name}.{name} should be bound.")
        else:
            hash_name = self.__get_typed_hash_name(hash_name, property_type)
            self.__update_vars.append(f"{_to_camel_case(name)}={hash_name}")
            self.__set_react_attribute(_to_camel_case(name), _get_client_var_name(hash_name))
        return self

    def set_attributes(self, attributes: t.List[tuple]):  # noqa: C901
        """
        TODO
        Sets the attributes from the property with type and default value.

        Arguments:

            attributes (list(tuple)): The list of attributes.
        """
        for attr in attributes:
            if not isinstance(attr, tuple):
                attr = (attr,)
            var_type = _get_tuple_val(attr, 1, PropertyType.string)
            if var_type == PropertyType.boolean:
                def_val = _get_tuple_val(attr, 2, False)
                val = self.__get_boolean_attribute(attr[0], def_val)
                if val != def_val:
                    self.set_boolean_attribute(attr[0], val)
            elif var_type == PropertyType.dynamic_boolean:
                self.__set_dynamic_bool_attribute(
                    attr[0], _get_tuple_val(attr, 2, False), _get_tuple_val(attr, 3, False)
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
                self.__set_list_attribute(
                    attr[0], self.__hashes.get(attr[0]), self.__attributes.get(attr[0]), str, False
                )
            elif var_type == PropertyType.function:
                self.__set_function_attribute(attr[0], _get_tuple_val(attr, 2, None), _get_tuple_val(attr, 3, True))
            elif var_type == PropertyType.react:
                self.__set_react_attribute(_to_camel_case(attr[0]), _get_tuple_val(attr, 2, None))
            elif var_type == PropertyType.string_or_number:
                self.__set_string_or_number_attribute(attr[0], _get_tuple_val(attr, 2, None))
            elif var_type == PropertyType.dict:
                self.set_dict_attribute(attr[0])
            elif var_type == PropertyType.dynamic_list:
                self.__set_dynamic_string_list(attr[0], _get_tuple_val(attr, 2, None))
            elif var_type == PropertyType.boolean_or_list:
                if _is_boolean(self.__attributes.get(attr[0])):
                    self.__set_dynamic_bool_attribute(attr[0], _get_tuple_val(attr, 2, False), True, update_main=False)
                else:
                    self.__set_dynamic_string_list(attr[0], _get_tuple_val(attr, 2, None))
            elif var_type == PropertyType.decimator:
                self.__set_decimator_attribute(attr_name=attr[0])
            elif var_type == PropertyType.data:
                self.__set_dynamic_property_without_default(attr[0], var_type)
            elif var_type == PropertyType.lov:
                self._get_adapter(attr[0])  # need to be called before set_lov
                self._set_lov(attr[0])
            elif var_type == PropertyType.lov_value:
                self.__set_dynamic_property_without_default(attr[0], var_type)
            self.__set_refresh_on_update()
        return self

    def set_attribute(self, name: str, value: t.Any):
        """
        TODO
        Sets an attribute.

        Arguments:

            name (str): The name of the attribute.
            value (Any): The value of the attribute (must be json serializable).
        """
        self.el.set(name, value)
        return self

    def get_element(self):
        """
        TODO
        Returns the xml.etree.ElementTree.Element
        """
        return self.el

    def _build_to_string(self):
        el_str = str(etree.tostring(self.el, encoding="utf8").decode("utf8"))
        el_str = el_str.replace("<?xml version='1.0' encoding='utf8'?>\n", "")
        el_str = el_str.replace("/>", ">")
        return el_str, self.__element_name
