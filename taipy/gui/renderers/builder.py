import datetime
import json
import numbers
import re
import typing as t
import warnings
import xml.etree.ElementTree as etree
from operator import attrgetter
from types import FunctionType

from ..page import Partial
from ..types import AttributeType
from ..utils import _MapDictionary, dateToISO, get_client_var_name, getDataType, is_boolean_true
from .jsonencoder import TaipyJsonEncoder
from .utils import _add_to_dict_and_get, _get_columns_dict, _get_tuple_val, _to_camel_case


class Builder:

    __keys: t.Dict[str, int] = {}

    __ONE_COLUMN_CHART = ["pie"]

    def __init__(
        self,
        control_type: str,
        element_name: str,
        attributes: t.Union[t.Dict[str, t.Any], None],
        default_value="<Empty>",
    ):
        from ..gui import Gui
        from .factory import Factory

        self.control_type = control_type
        self.element_name = element_name
        self.attributes = attributes or {}
        self.__hashes = {}
        self.__update_vars: t.List[str] = []
        self.el = etree.Element(element_name)
        self._gui = Gui._get_instance()

        self.default_property_name = Factory.get_default_property_name(control_type) or ""
        default_property_value = self.attributes.get(self.default_property_name, None)
        if default_property_value is None:
            self.attributes[self.default_property_name] = default_value

        # Bind properties dictionary to attributes if condition is matched (will leave the binding for function at the builder )
        if "properties" in self.attributes:
            (properties_dict_name, _) = self.__parse_attribute_value(self.attributes["properties"])
            self._gui.bind_var(properties_dict_name)
            properties_dict = getattr(self._gui, properties_dict_name)
            if not isinstance(properties_dict, _MapDictionary):
                raise Exception(
                    f"Can't find properties configuration dictionary {properties_dict_name}!"
                    f" Please review your GUI templates!"
                )
            # Iterate through properties_dict and append to self.attributes
            for k, v in properties_dict.items():
                self.attributes[k] = v

        # Bind potential function and expressions in self.attributes
        for k, v in self.attributes.items():
            # need to unescape the double quotes that were escaped during preprocessing
            (val, hashname) = self.__parse_attribute_value(v.replace('\\"', '"') if isinstance(v, str) else v)
            if isinstance(val, str):
                # Bind potential function
                self._gui.bind_func(val)
            # Try to evaluate as expressions
            if val is not None or hashname:
                self.attributes[k] = val
            if hashname:
                self.__hashes[k] = hashname
        # set classname
        self.__set_classNames()
        # define a unique key
        self.set_attribute("key", Builder._get_key(self.element_name))

    @staticmethod
    def __to_string(x: t.Any) -> str:
        return str(x)

    @staticmethod
    def _get_key(name: str) -> str:
        key_index = Builder.__keys.get(name, 0)
        Builder.__keys[name] = key_index + 1
        return f"{name}.{key_index}"

    @staticmethod
    def _reset_key() -> None:
        Builder.__keys = {}

    def __get_list_of_(self, name: str):
        lof = self.attributes.get(name)
        if isinstance(lof, str):
            self.from_string = True
            lof = [s for s in lof.split(";")]
        return lof

    def __get_name_indexed_property(self, name: str) -> t.Dict[str, t.Any]:
        ret = {}
        index_re = re.compile(name + r"\[(.*)\]$")
        for key in self.attributes.keys():
            m = index_re.match(key)
            if m:
                ret[m.group(1)] = self.attributes.get(key)
        return ret

    def __get_multiple_indexed_attributes(self, names: t.Tuple[str], index: t.Optional[int] = None) -> t.List[str]:
        names = [n if index is None else f"{n}[{index}]" for n in names]  # type: ignore
        return [self.attributes.get(name) for name in names]

    def __parse_attribute_value(self, value) -> t.Tuple:
        if isinstance(value, str) and self._gui._is_expression(value):
            hash_value = self._gui._evaluate_expr(value, get_hash=True)
            try:
                return (attrgetter(hash_value)(self._gui._get_data_scope()), hash_value)
            except AttributeError:
                warnings.warn(f"Expression '{value}' cannot be evaluated")
        return (value, None)

    def __get_boolean_attribute(self, name: str, default_value=False):
        boolattr = self.attributes.get(name, default_value)
        return is_boolean_true(boolattr) if isinstance(boolattr, str) else bool(boolattr)

    def __set_boolean_attribute(self, name: str, value: bool):
        return self.__set_react_attribute(_to_camel_case(name), value)

    def __set_dict_attribute(self, name: str):
        dict_attr = self.attributes.get(name)
        if dict_attr:
            if isinstance(dict_attr, str):
                vals = [x.strip().split(":") for x in dict_attr.split(";")]
                dict_attr = {}
                for val in vals:
                    if len(val) > 1:
                        value = val[1].strip()
                        self._gui.bind_func(value)
                        dict_attr[val[0].strip()] = value
            if isinstance(dict_attr, (dict, _MapDictionary)):
                self.__set_json_attribute(_to_camel_case(name), dict_attr)
            else:
                warnings.warn(f"{self.element_name} {name} should be a dict\n'{str(dict_attr)}'")
        return self

    def __set_json_attribute(self, name, value):
        return self.set_attribute(name, json.dumps(value, cls=TaipyJsonEncoder))

    def __set_list_of_(self, name: str):
        lof = self.__get_list_of_(name)
        if not isinstance(lof, (list, tuple)):
            if lof is not None:
                warnings.warn(f"{self.element_name} {name} should be a list")
            return self
        return self.__set_json_attribute(_to_camel_case(name), lof)

    def __set_number_attribute(
        self, name: str, default_value: t.Optional[str] = None, optional: t.Optional[bool] = True
    ):
        value = self.attributes.get(name, default_value)
        if value is None:
            if not optional:
                warnings.warn(f"Property {name} is required for control {self.control_type}")
            return self
        try:
            val = float(value)
        except ValueError:
            raise ValueError(f"Property {name} expects a number for control {self.control_type}")
        return self.__set_react_attribute(_to_camel_case(name), val)

    def __set_string_attribute(
        self, name: str, default_value: t.Optional[str] = None, optional: t.Optional[bool] = True
    ):
        strattr = self.attributes.get(name, default_value)
        if strattr is None:
            if not optional:
                warnings.warn(f"Property {name} is required for control {self.control_type}")
            return self
        return self.set_attribute(_to_camel_case(name), strattr)

    def __set_string_or_number_attribute(self, name: str, default_value: t.Optional[t.Any] = None):
        attr = self.attributes.get(name, default_value)
        if attr is None:
            return self
        if isinstance(attr, numbers.Number):
            return self.__set_react_attribute(_to_camel_case(name), attr)
        else:
            return self.set_attribute(_to_camel_case(name), attr)

    def __set_react_attribute(self, name: str, value: t.Any):
        return self.set_attribute(name, "{!" + (str(value).lower() if isinstance(value, bool) else str(value)) + "!}")

    def get_adapter(self, var_name: str, property_name: t.Optional[str] = None, multi_selection=True):  # noqa: C901
        property_name = var_name if property_name is None else property_name
        lov = self.__get_list_of_(var_name)
        if isinstance(lov, list):
            from_string = getattr(self, "from_string", False)
            adapter = self.attributes.get("adapter")
            if adapter and not isinstance(adapter, FunctionType):
                warnings.warn("'adapter' property value is invalid")
                adapter = None
            var_type = self.attributes.get("type")
            if isinstance(var_type, t.Type):  # type: ignore
                var_type = var_type.__name__
            if not isinstance(var_type, str):
                elt = None
                if len(lov) == 0:
                    value = self.attributes.get("value")
                    if isinstance(value, list):
                        if len(value) > 0:
                            elt = value[0]
                    else:
                        elt = value
                else:
                    elt = lov[0]
                var_type = type(elt).__name__ if elt is not None else None
            if adapter is None:
                adapter = self._gui._get_adapter_for_type(var_type)
            lov_name = self.__hashes.get(var_name)
            if lov_name:
                if adapter is None:
                    adapter = self._gui._get_adapter_for_type(lov_name)
                else:
                    self._gui._add_type_for_var(lov_name, var_type)
            value_name = self.__hashes.get("value")
            if value_name:
                if adapter is None:
                    adapter = self._gui._get_adapter_for_type(value_name)
                else:
                    self._gui._add_type_for_var(value_name, var_type)
            if adapter is not None:
                self._gui._add_adapter_for_type(var_type, adapter)

            if adapter is None:
                adapter = (lambda x: (x, x)) if from_string else (lambda x: str(x))  # type: ignore
            ret_list = []
            if len(lov) > 0:
                ret = self._gui._get_valid_adapter_result(lov[0], index="0")
                if ret is None:  # lov list is not a list of tuple(id, label)
                    for idx, elt in enumerate(lov):
                        ret = self._gui._run_adapter(adapter, elt, adapter.__name__, str(idx))
                        if ret is not None:
                            ret_list.append(ret)
                else:
                    ret_list = lov
            self.attributes["default_" + property_name] = ret_list

            ret_list = []
            value = self.attributes.get("value")
            val_list = value if isinstance(value, list) else [value]
            for val in val_list:
                ret = self._gui._run_adapter(adapter, val, adapter.__name__, "-1", id_only=True)
                if ret is not None:
                    ret_list.append(ret)
            if multi_selection:
                self.__set_default_value("value", ret_list)
            else:
                ret_val = ret_list[0] if len(ret_list) else ""
                if ret_val == "-1" and self.attributes.get("unselected_value") is not None:
                    ret_val = self.attributes.get("unselected_value")
                self.__set_default_value("value", ret_val)
        return self

    def __update_col_desc_from_indexed(self, columns: t.Dict[str, t.Any], name: str):
        col_value = self.__get_name_indexed_property(name)
        for k, v in col_value.items():
            col_desc = next((x for x in columns.values() if x["dfid"] == k), None)
            if col_desc:
                if col_desc.get(_to_camel_case(name)) is None:
                    col_desc[_to_camel_case(name)] = str(v)
            else:
                warnings.warn(f"{self.element_name} {name}[{k}] is not in the list of displayed columns")

    def get_dataframe_attributes(self, date_format="MM/dd/yyyy", number_format=None):  # noqa: C901
        value = self.attributes.get("data")

        col_types = self._gui._accessors._get_col_types(self.__hashes.get("data", ""), value)
        columns = _get_columns_dict(
            value,
            _add_to_dict_and_get(self.attributes, "columns", {}),
            col_types,
            _add_to_dict_and_get(self.attributes, "date_format", date_format),
            _add_to_dict_and_get(self.attributes, "number_format", number_format),
        )
        if columns is not None:
            self.__update_col_desc_from_indexed(columns, "nan_value")
            self.__update_col_desc_from_indexed(columns, "width")
            group_by = self.__get_name_indexed_property("group_by")
            for k, v in group_by.items():
                if is_boolean_true(v):
                    col_desc = next((x for x in columns.values() if x["dfid"] == k), None)
                    if col_desc:
                        col_desc["groupBy"] = True
                    else:
                        warnings.warn(f"{self.element_name} group_by[{k}] is not in the list of displayed columns")
            apply = self.__get_name_indexed_property("apply")
            for k, v in apply.items():
                col_desc = next((x for x in columns.values() if x["dfid"] == k), None)
                if col_desc:
                    if isinstance(v, FunctionType):
                        value = self.__hashes.get(f"apply[{k}]")
                        # bind the function to its hashed value
                        self._gui.bind_var_val(value, v)
                    else:
                        value = str(v).strip()
                        if value and value not in self._gui._agregate_functions:
                            # Bind potential function
                            self._gui.bind_func(value)
                    if value:
                        col_desc["apply"] = value
                else:
                    warnings.warn(f"{self.element_name} apply[{k}] is not in the list of displayed columns")
            line_style = self.attributes.get("style")
            if line_style:
                if isinstance(line_style, FunctionType):
                    value = self.__hashes.get("style")
                    # bind the function to its hashed value
                    self._gui.bind_var_val(value, line_style)
                else:
                    value = str(line_style).strip()
                    if value:
                        # Bind potential function
                        self._gui.bind_func(value)
                if value in col_types.keys():
                    warnings.warn(f"{self.element_name} style={value} cannot be a column's name")
                elif value:
                    self.set_attribute("lineStyle", value)
            styles = self.__get_name_indexed_property("style")
            for k, v in styles.items():
                col_desc = next((x for x in columns.values() if x["dfid"] == k), None)
                if col_desc:
                    if isinstance(v, FunctionType):
                        value = self.__hashes.get(f"style[{k}]")
                        # bind the function to its hashed value
                        self._gui.bind_var_val(value, v)
                    else:
                        value = str(v).strip()
                        if value:
                            # Bind potential function
                            self._gui.bind_func(value)
                    if value in col_types.keys():
                        warnings.warn(f"{self.element_name} style[{k}]={value} cannot be a column's name")
                    elif value:
                        col_desc["style"] = value
                else:
                    warnings.warn(f"{self.element_name} style[{k}] is not in the list of displayed columns")
            self.attributes["columns"] = columns
            self.__set_json_attribute("columns", columns)
        return self

    def __check_dict(self, values: t.List[t.Any], index: int, names: t.Tuple[str]) -> None:
        if values[index] is not None and not isinstance(values[index], (dict, _MapDictionary)):
            warnings.warn(f"{self.element_name} {names[index]} should be a dict")
            values[index] = None

    def get_chart_config(self, default_type="scatter", default_mode="lines+markers"):
        names = (
            "x",
            "y",
            "z",
            "label",
            "text",
            "mode",
            "type",
            "color",
            "xaxis",
            "yaxis",
            "selected_color",
            "marker",
            "selected_marker",
            "orientation",
            "name",
            "line",
            "text_anchor",
        )
        trace = self.__get_multiple_indexed_attributes(names)
        if not trace[5]:
            # mode
            trace[5] = default_mode
        if not trace[6]:
            # type
            trace[6] = default_type
        else:
            trace[6] = str(trace[6]).strip().lower()
        if not trace[8]:
            # xaxis
            trace[8] = "x"
        if not trace[9]:
            # yaxis
            trace[9] = "y"
        self.__check_dict(trace, 11, names)
        self.__check_dict(trace, 12, names)
        traces = []
        idx = 1
        indexed_trace = self.__get_multiple_indexed_attributes(names, idx)
        if len([x for x in indexed_trace if x]):
            while len([x for x in indexed_trace if x]):
                self.__check_dict(indexed_trace, 11, names)
                self.__check_dict(indexed_trace, 12, names)
                traces.append([x or trace[i] for i, x in enumerate(indexed_trace)])
                idx += 1
                indexed_trace = self.__get_multiple_indexed_attributes(names, idx)
        else:
            traces.append(trace)
        # filter traces where we don't have at least x and y
        traces = [t for t in traces if t[0] and (t[6] in Builder.__ONE_COLUMN_CHART or t[1])]
        if not len(traces) and trace[0] and trace[1]:
            traces.append(trace)

        # configure columns
        columns = set()
        for trace in traces:
            columns.update([t for t in trace[0:5] if t])
        value = self.attributes.get("data")
        columns = _get_columns_dict(value, list(columns), self._gui._accessors._get_col_types("", value))
        if columns is not None:
            self.attributes["columns"] = columns
            reverse_cols = {cd["dfid"]: c for c, cd in columns.items()}

            ret_dict = {
                "columns": columns,
                "labels": [reverse_cols.get(t[3], (t[3] or "")) for t in traces],
                "texts": [reverse_cols.get(t[4], (t[4] or None)) for t in traces],
                "modes": [t[5] for t in traces],
                "types": [t[6] for t in traces],
                "xaxis": [t[8] for t in traces],
                "yaxis": [t[9] for t in traces],
                "markers": [t[11] or ({"color": t[7]} if t[7] else None) for t in traces],
                "selectedMarkers": [t[12] or ({"color": t[10]} if t[10] else None) for t in traces],
                "traces": [[reverse_cols.get(c, c) for c in [t[0], t[1], t[2]]] for t in traces],
                "orientations": [t[13] for t in traces],
                "names": [t[14] for t in traces],
                "lines": [t[15] if isinstance(t[15], dict) else {"dash": t[15]} for t in traces],
                "textAnchors": [t[16] for t in traces],
            }

            self.__set_json_attribute("config", ret_dict)
            self.set_chart_selected(max=len(traces))
        return self

    def set_chart_layout(self):
        layout = self.attributes.get("layout")
        if layout:
            if isinstance(layout, (dict, _MapDictionary)):
                self.__set_json_attribute("layout", layout)
            else:
                warnings.warn(f"Chart control: layout attribute should be a dict\n'{str(layout)}'")

    def set_string_with_check(self, var_name: str, values: t.List[str], default_value: t.Optional[str] = None):
        value = self.attributes.get(var_name, default_value)
        if value is not None:
            value = str(value).lower()
            self.attributes[var_name] = value
            if value not in values:
                warnings.warn(f"{self.element_name} {var_name}={value} should be in {values}")
            else:
                self.__set_string_attribute(var_name, default_value)
        return self

    def __set_list_attribute(self, name: str, hash_name: t.Optional[str], val: t.Any, elt_type: t.Type) -> t.List[str]:
        if not hash_name and isinstance(val, str):
            val = [elt_type(t.strip()) for t in val.split(";")]
        if isinstance(val, list):
            if hash_name:
                self.__set_react_attribute(name, hash_name)
                return [f"{name}={hash_name}"]
            else:
                self.__set_json_attribute(name, val)
        else:
            warnings.warn(f"{self.element_name} {name} should be a list of {elt_type}")
        return []

    def set_chart_selected(self, max=0):
        name = "selected"
        default_sel = self.attributes.get(name)
        idx = 1
        name_idx = f"{name}[{idx}]"
        sel = self.attributes.get(name_idx)
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
            sel = self.attributes.get(name_idx)

    def get_list_attribute(self, name: str, list_type: AttributeType):
        varname = self.__hashes.get(name)
        if varname is None:
            list_val = self.attributes.get(name)
            if isinstance(list_val, str):
                list_val = [s for s in list_val.split(";")]
            if isinstance(list_val, list):
                # TODO catch the cast exception
                if list_type.value == AttributeType.number.value:
                    list_val = [int(v) for v in list_val]
                else:
                    list_val = [int(v) for v in list_val]
            else:
                if list_val is not None:
                    warnings.warn(f"{self.element_name} {name} should be a list")
                list_val = []
            self.__set_react_attribute(_to_camel_case(name), list_val)
        else:
            self.__set_react_attribute(_to_camel_case(name), varname)
        return self

    def __set_classNames(self):
        classes = ["taipy-" + self.control_type.replace("_", "-")]
        cl = self._gui._config.style_config.get(self.control_type)
        if cl:
            classes.append(cl)
        cl = self.attributes.get("classname")
        if cl:
            classes.append(str(cl))

        return self.set_attribute("className", " ".join(classes))

    def set_dataType(self):
        value = self.attributes.get("value")
        return self.set_attribute("dataType", getDataType(value))

    def set_file_content(self, var_name: str = "content"):
        hash_name = self.__hashes.get(var_name)
        if hash_name:
            self.__set_tp_varname(hash_name)
        else:
            warnings.warn("{self.element_name} {var_name} should be binded")
        return self

    def set_content(self, var_name: str = "content", image=True):
        content = self.attributes.get(var_name)
        hash_name = self.__hashes.get(var_name)
        if content is None and not hash_name:
            return self
        value = self._gui._get_content(hash_name or var_name, content, hash_name is not None, image)
        if hash_name is not None:
            self.__set_react_attribute(
                var_name,
                get_client_var_name(hash_name),
            )
            self.__set_tp_varname(hash_name)
        return self.set_attribute(_to_camel_case("default_" + var_name), value)

    def set_lov(self, var_name="lov", property_name: t.Optional[str] = None):
        property_name = var_name if property_name is None else property_name
        self.__set_list_of_("default_" + property_name)
        hash_name = self.__hashes.get(var_name)
        if hash_name:
            self.__update_vars.append(f"{property_name}={hash_name}")
            self.__set_react_attribute(property_name, hash_name)
        return self

    def __set_dynamic_string_list(self, var_name: str, default_value: t.Any):
        hash_name = self.__hashes.get(var_name)
        loi = self.attributes.get(var_name)
        if loi is None:
            loi = default_value
        if isinstance(loi, str):
            loi = [s.strip() for s in loi.split(";") if s.strip()]
        if isinstance(loi, list):
            self.__set_json_attribute(_to_camel_case("default_" + var_name), loi)
        if hash_name:
            self.__update_vars.append(f"{var_name}={hash_name}")
            self.__set_react_attribute(var_name, hash_name)
        return self

    def __set_dynamic_number_attribute(self, var_name: str, default_value: t.Any):
        hash_name = self.__hashes.get(var_name)
        numVal = self.attributes.get(var_name)
        if numVal is None:
            numVal = default_value
        if isinstance(numVal, str):
            try:
                numVal = float(numVal)
            except Exception as e:
                warnings.warn(f"{self.element_name} {var_name} cannot be transformed into a number\n{e}")
                numVal = 0
        if isinstance(numVal, numbers.Number):
            self.__set_react_attribute(_to_camel_case("default_" + var_name), numVal)
        elif numVal is not None:
            warnings.warn(f"{self.element_name} {var_name} value is not not valid {numVal}")
        if hash_name:
            self.__update_vars.append(f"{var_name}={hash_name}")
            self.__set_react_attribute(var_name, hash_name)
        return self

    def __set_default_value(self, var_name: str, value: t.Optional[t.Any] = None, native_type: bool = False):
        if value is None:
            value = self.attributes.get(var_name)
        default_var_name = _to_camel_case("default_" + var_name)
        if isinstance(value, datetime.datetime):
            self.set_attribute(default_var_name, dateToISO(value))
        elif isinstance(value, str):
            self.set_attribute(default_var_name, value)
        elif native_type and isinstance(value, numbers.Number):
            self.__set_react_attribute(default_var_name, value)
        elif value is None:
            self.__set_react_attribute(default_var_name, "null")
        else:
            self.__set_json_attribute(default_var_name, value)
        return self

    def __set_tp_varname(self, hash_name: str):
        return self.set_attribute("tp_varname", self._gui._get_expr_from_hash(hash_name))

    def set_value_and_default(
        self,
        var_name: t.Optional[str] = None,
        with_update=True,
        with_default=True,
        native_type: bool = False,
    ):
        var_name = self.default_property_name if var_name is None else var_name
        hash_name = self.__hashes.get(var_name)
        if hash_name:
            self.__set_react_attribute(
                var_name,
                get_client_var_name(hash_name),
            )
            if with_update:
                self.__set_tp_varname(hash_name)
            if with_default:
                if native_type:
                    val = self.attributes.get(var_name)
                    if native_type and isinstance(val, str):
                        try:
                            val = float(val)
                        except Exception:
                            # keep as str
                            pass
                    self.__set_default_value(var_name, val, native_type=native_type)
                else:
                    self.__set_default_value(var_name)
        else:
            value = self.attributes.get(var_name)
            if value is not None:
                if native_type:
                    if isinstance(value, str):
                        try:
                            value = float(value)
                        except Exception:
                            # keep as str
                            pass
                    if isinstance(value, (int, float)):
                        return self.__set_react_attribute(var_name, value)
                self.set_attribute(var_name, value)
        return self

    def set_labels(self, var_name: str = "labels"):
        value = self.attributes.get(var_name)
        if value:
            if is_boolean_true(value):
                return self.__set_react_attribute(_to_camel_case(var_name), True)
            return self.__set_dict_attribute(var_name)
        return self

    def set_page_id(self):
        return self.__set_string_attribute("page_id")

    def set_partial(self):
        if self.element_name != "Dialog" and self.element_name != "Pane":
            return self
        partial = self.attributes.get("partial")
        if partial:
            page_id = self.attributes.get("page_id")
            if page_id:
                warnings.warn("Dialog control: page_id and partial should not be defined at the same time")
            if isinstance(partial, Partial):
                self.attributes["page_id"] = partial.route
        return self

    def set_propagate(self):
        val = self.__get_boolean_attribute("propagate", self._gui._config.app_config.get("propagate"))
        if not val:
            return self.__set_boolean_attribute("propagate", False)
        return self

    def set_refresh(self):
        return self.__set_react_attribute(
            "refresh",
            get_client_var_name(self.__hashes.get(self.default_property_name, self.default_property_name) + ".refresh"),
        )

    def set_refresh_on_update(self):
        if len(self.__update_vars):
            self.set_attribute("tp_updatevars", ";".join(self.__update_vars))
        return self

    def set_table_pagesize_options(self, default_size=[50, 100, 500]):
        page_size_options = self.attributes.get("page_size_options", default_size)
        if isinstance(page_size_options, str):
            try:
                page_size_options = [int(s.strip()) for s in page_size_options.split(";")]
            except Exception as e:
                warnings.warn(f"{self.element_name} page_size_options: invalid value {page_size_options}\n{e}")
        if isinstance(page_size_options, list):
            self.__set_json_attribute("pageSizeOptions", page_size_options)
        else:
            warnings.warn(f"{self.element_name} page_size_options should be a list")
        return self

    def set_type(self, type_name: str):
        self.type_name = type_name
        self.set_attribute("type", type_name)
        return self

    def set_kind(self):
        theme = self.attributes.get("theme", False)
        if theme:
            self.set_attribute("kind", "theme")
        return self

    def set_attributes(self, attributes: t.List[tuple]):
        for attr in attributes:
            if not isinstance(attr, tuple):
                attr = (attr,)
            type = _get_tuple_val(attr, 1, AttributeType.string)
            if type == AttributeType.boolean:
                def_val = _get_tuple_val(attr, 2, False)
                val = self.__get_boolean_attribute(attr[0], def_val)
                if val != def_val:
                    self.__set_boolean_attribute(attr[0], val)
            elif type == AttributeType.dynamic_boolean:
                hash_name = self.__hashes.get(attr[0])
                def_val = _get_tuple_val(attr, 2, False)
                val = self.__get_boolean_attribute(attr[0], def_val)
                default_name = "default_" + attr[0] if hash_name is not None else attr[0]
                if val != def_val:
                    self.__set_boolean_attribute(default_name, val)
                if hash_name is not None:
                    self.__set_react_attribute(_to_camel_case(attr[0]), get_client_var_name(hash_name))
            elif type == AttributeType.number:
                self.__set_number_attribute(attr[0], _get_tuple_val(attr, 2, None))
            elif type == AttributeType.dynamic_number:
                self.__set_dynamic_number_attribute(attr[0], _get_tuple_val(attr, 2, None))
            elif type == AttributeType.string:
                self.__set_string_attribute(attr[0], _get_tuple_val(attr, 2, None), _get_tuple_val(attr, 3, True))
            elif type == AttributeType.react:
                self.__set_react_attribute(_to_camel_case(attr[0]), _get_tuple_val(attr, 2, None))
            elif type == AttributeType.string_or_number:
                self.__set_string_or_number_attribute(attr[0], _get_tuple_val(attr, 2, None))
            elif type == AttributeType.dict:
                self.__set_dict_attribute(attr[0])
            elif type == AttributeType.dynamic_list:
                self.__set_dynamic_string_list(attr[0], _get_tuple_val(attr, 2, None))
        return self

    def set_attribute(self, name, value):
        if name.startswith("on"):
            name = "tp_" + name
        self.el.set(name, value)
        return self

    def build_to_string(self):
        el_str = str(etree.tostring(self.el, encoding="utf8").decode("utf8"))
        el_str = el_str.replace("<?xml version='1.0' encoding='utf8'?>\n", "")
        el_str = el_str.replace("/>", ">")
        return el_str, self.element_name
