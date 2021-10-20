import datetime
import json
import typing as t
import warnings
import numbers
from operator import attrgetter
from types import FunctionType

from markdown.util import etree

from ..page import Partial
from ..utils import _get_dict_value, _MapDictionary, dateToISO, get_client_var_name, getDataType, is_boolean_true
from ..wstype import AttributeType
from .jsonencoder import TaipyJsonEncoder
from .utils import _add_to_dict_and_get, _get_columns_dict, _to_camel_case


class Builder:

    __keys: dict[str, int] = {}

    def __init__(
        self,
        control_type,
        element_name,
        attributes,
        default_value="<Empty>",
    ):
        from ..gui import Gui
        from .factory import Factory

        self.control_type = control_type
        self.element_name = element_name
        self.attributes = attributes or {}
        self.__hashes = {}
        self.value = default_value
        self.el = etree.Element(element_name)
        self._gui = Gui._get_instance()
        # Whether this object has been evaluated (by expression) in preprocessor
        self.has_evaluated = False
        default_property_name = Factory.get_default_property_name(control_type)
        default_property_value = self.attributes.get(default_property_name)
        if default_property_value:
            if isinstance(default_property_value, str) and self._gui._is_expression(default_property_value):
                self.has_evaluated = True
                default_property_value = self._gui._fetch_expression_list(default_property_value)[0]
                self.value = attrgetter(default_property_value)(self._gui._values)
                self.expr_hash = default_property_value
                self.expr = self._gui._hash_to_expr[self.expr_hash]
            else:
                self.value = self.expr_hash = self.expr = default_property_value

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

        # Bind potential function in self.attributes
        for k, v in self.attributes.items():
            (val, hashname) = self.__parse_attribute_value(v)
            if isinstance(val, str):
                # Bind potential function
                self._gui.bind_func(val)
            # Try to evaluate as expressions
            if val is not None:
                self.attributes[k] = val
            if hashname:
                self.__hashes[k] = hashname
        # define a unique key
        self.set_attribute("key", Builder._get_key(self.expr))

    @staticmethod
    def __to_string(x: t.Any) -> str:
        return str(x)

    @staticmethod
    def _get_key(name: str) -> str:
        key_index = _get_dict_value(Builder.__keys, name)
        Builder.__keys[name] = (key_index or 0) + 1
        return name + "." + (str(key_index) if key_index else "0")

    def __get_list_of_(self, name: str):
        lof = self.__get_property(name)
        if isinstance(lof, str):
            self.from_string = True
            lof = [(s, s) for s in lof.split(";")]
        return lof

    def __get_property(self, name: str, default_value: t.Any = None) -> t.Any:
        prop = _get_dict_value(self.attributes, name)
        if prop is None:
            prop = default_value
        return prop

    def __get_multiple_indexed_attributes(self, names: t.Tuple[str], index: t.Optional[int] = None) -> t.List[str]:
        names = [n if index is None else (n + "[" + str(index) + "]") for n in names]
        return [self.__get_property(name) for name in names]

    def __parse_attribute_value(self, value) -> t.Tuple:
        if isinstance(value, str) and self._gui._is_expression(value):
            hash_value = self._gui._fetch_expression_list(value)[0]
            self._gui.bind_var(hash_value)
            try:
                return (attrgetter(hash_value)(self._gui._values), hash_value)
            except AttributeError as ae:
                warnings.warn(f"Expression '{value}' cannot be evaluated")
        return (value, None)

    def __set_boolean_attribute(self, name: str, default_value=False):
        boolattr = self.__get_property(name, default_value)
        if isinstance(boolattr, str):
            boolattr = is_boolean_true(boolattr)
        return self.__set_react_attribute(_to_camel_case(name), boolattr)

    def __set_json_attribute(self, name, value):
        return self.set_attribute(name, json.dumps(value, cls=TaipyJsonEncoder))

    def __set_list_of_(self, name: str):
        lof = self.__get_list_of_(name)
        if not isinstance(lof, (list, tuple)):
            warnings.warn(f"Component {self.element_name} Attribute {name}: should be a string or a list")
            return self
        return self.__set_json_attribute(_to_camel_case(name), lof)

    def __set_string_attribute(
        self, name: str, default_value: t.Optional[str] = None, optional: t.Optional[bool] = True
    ):
        strattr = self.__get_property(name, default_value)
        if strattr is None:
            if not optional:
                warnings.warn(f"property {name} is required for component {self.control_type}")
            return self
        return self.set_attribute(_to_camel_case(name), strattr)

    def __set_string_or_number_attribute(self, name: str, default_value: t.Optional[t.Any] = None):
        attr = self.__get_property(name, default_value)
        if attr is None:
            return self
        if isinstance(attr, numbers.Number):
            return self.__set_react_attribute(_to_camel_case(name), attr)
        else:
            return self.set_attribute(_to_camel_case(name), attr)

    def __set_react_attribute(self, name: str, value: t.Any):
        return self.set_attribute(name, "{!" + (str(value).lower() if isinstance(value, bool) else str(value)) + "!}")

    def get_adapter(self, property_name: str):  # noqa: C901
        lov = self.__get_list_of_(property_name)
        from_string = hasattr(self, "from_string") and self.from_string
        if isinstance(lov, list):
            adapter = self.__get_property("adapter")
            if not isinstance(adapter, FunctionType):
                if adapter:
                    warnings.warn("Component Selector Attribute Adapter is invalid")
                adapter = None
            var_type = self.__get_property("type")
            if isinstance(var_type, t.Type):  # type: ignore
                var_type = var_type.__name__
            if not isinstance(var_type, str):
                elt = None
                if len(lov) == 0:
                    if isinstance(self.value, list):
                        if len(self.value) > 0:
                            elt = self.value[0]
                    else:
                        elt = self.value
                else:
                    elt = lov[0]
                var_type = type(elt).__name__ if elt is not None else None
            if adapter is None:
                adapter = self._gui._get_adapter_for_type(var_type)
            lov_name = _get_dict_value(self.__hashes, property_name)
            if lov_name:
                if adapter is None:
                    adapter = self._gui._get_adapter_for_type(lov_name)
                else:
                    self._gui.add_type_for_var(lov_name, var_type)
            value_name = _get_dict_value(self.__hashes, "value")
            if value_name:
                if adapter is None:
                    adapter = self._gui._get_adapter_for_type(value_name)
                else:
                    self._gui.add_type_for_var(value_name, var_type)
            if adapter is not None:
                self._gui.add_adapter_for_type(var_type, adapter)

            if adapter is None:
                adapter = (lambda x: (x, x)) if from_string else (lambda x: str(x))  # type: ignore
            ret_list = []
            if len(lov) > 0:
                ret = self._gui._get_valid_adapter_result(lov[0], index=0)
                if ret is None:  # lov list is not a list of tuple(id, label)
                    for idx, elt in enumerate(lov):
                        ret = self._gui._run_adapter(adapter, elt, adapter.__name__, idx)
                        if ret is not None:
                            ret_list.append(ret)
                else:
                    ret_list = lov
            self.attributes["default_lov"] = ret_list

            ret_list = []
            val_list = self.value if isinstance(self.value, list) else [self.value]
            for val in val_list:
                ret = self._gui._run_adapter(adapter, val, adapter.__name__, -1, id_only=True)
                if ret is not None:
                    ret_list.append(ret)
            self.set_default_value(ret_list)
        return self

    def get_dataframe_attributes(self, date_format="MM/dd/yyyy", number_format=None):
        columns = _get_columns_dict(
            self.value,
            _add_to_dict_and_get(self.attributes, "columns", {}),
            self._gui._data_accessors._get_col_types("", self.value),
            _add_to_dict_and_get(self.attributes, "date_format", date_format),
            _add_to_dict_and_get(self.attributes, "number_format", number_format),
        )
        if columns is not None:
            self.attributes["columns"] = columns
            self.__set_json_attribute("columns", columns)
        return self

    def get_chart_attributes(self, default_type="scatter", default_mode="lines+markers"):
        names = ("x", "y", "z", "label", "mode", "type", "color", "xaxis", "yaxis")
        trace = self.__get_multiple_indexed_attributes(names)
        if not trace[4]:
            # mode
            trace[4] = default_mode
        if not trace[5]:
            # type
            trace[5] = default_type
        if not trace[7]:
            # xaxis
            trace[7] = "x"
        if not trace[8]:
            # yaxis
            trace[8] = "y"
        traces = []
        idx = 1
        indexed_trace = self.__get_multiple_indexed_attributes(names, idx)
        while len([x for x in indexed_trace if x]):
            traces.append([x or trace[i] for i, x in enumerate(indexed_trace)])
            idx += 1
            indexed_trace = self.__get_multiple_indexed_attributes(names, idx)
        # filter traces where we don't have at least x and y
        traces = [t for t in traces if t[0] and t[1]]
        if not len(traces) and trace[0] and trace[1]:
            traces.append(trace)

        # configure columns
        columns = set()
        for trace in traces:
            columns.update([t for t in trace[0:4] if t])
        columns = _get_columns_dict(self.value, list(columns), self._gui._data_accessors._get_col_types("", self.value))
        if columns is not None:
            self.attributes["columns"] = columns
            self.__set_json_attribute("columns", columns)

            reverse_cols = {cd["dfid"]: c for c, cd in columns.items()}

            labels = [reverse_cols[t[3]] if t[3] in reverse_cols else (t[3] or "") for t in traces]
            if len(labels):
                self.__set_json_attribute("labels", labels)
            self.__set_json_attribute("modes", [t[4] for t in traces])
            self.__set_json_attribute("types", [t[5] for t in traces])
            self.__set_json_attribute("colors", [(t[6] or "") for t in traces])
            self.__set_json_attribute("axis", [(t[7], t[8]) for t in traces])
            traces = [[reverse_cols[c] if c in reverse_cols else c for c in [t[0], t[1], t[2]]] for t in traces]
            self.__set_json_attribute("traces", traces)
        return self

    def set_chart_layout(self):
        layout = _get_dict_value(self.attributes, "layout")
        if layout:
            if isinstance(layout, (dict, _MapDictionary)):
                self.__set_json_attribute("layout", layout)
            else:
                warnings.warn(f"Chart: layout attribute should be a dict\n'{str(layout)}'")

        return self

    def set_className(self, class_name="", config_class="input"):
        from ..gui import Gui

        self.set_attribute(
            "className",
            class_name + " " + self._gui._config.style_config[config_class],
        )
        return self

    def set_dataType(self):
        self.set_attribute("dataType", getDataType(self.value))
        return self

    def set_default_lov(self):
        return self.__set_list_of_("default_lov")

    def set_default_value(self, value: t.Optional[t.Any] = None):
        if value is None:
            value = self.value
        if isinstance(value, datetime.datetime):
            self.set_attribute("defaultValue", dateToISO(value))
        elif isinstance(value, str):
            self.set_attribute("defaultValue", value)
        else:
            self.__set_json_attribute("defaultValue", value)
        return self

    def set_expresion_hash(self):
        if self.has_evaluated:
            self.__set_react_attribute(
                "value",
                get_client_var_name(self.expr_hash),
            )
            self.set_attribute("tp_varname", self.expr)
        else:
            self.set_attribute("value", self.value)
        return self

    def set_page_id(self):
        return self.__set_string_attribute("page_id", optional=False)

    def set_partial(self):
        if self.element_name != "Dialog":
            return self
        partial = self.__get_property("partial")
        if partial:
            page_id = self.__get_property("page_id")
            if page_id:
                warnings.warn("Dialog control: page_id and partial should not be defined at the same time")
            if isinstance(partial, Partial):
                self.attributes["page_id"] = partial.route
        return self

    def set_propagate(self):
        from ..gui import Gui

        return self.__set_boolean_attribute("propagate", self._gui._config.app_config["propagate"])

    def set_refresh(self):
        return self.__set_react_attribute("refresh", get_client_var_name(self.expr_hash + ".refresh"))

    def set_refresh_on_update(self, name=None):
        if name:
            if not isinstance(name, (tuple, list)):
                name = [name]
            name_list = []
            for nm in name:
                varname = _get_dict_value(self.__hashes, nm)
                if varname:
                    name_list.append(varname)
                self.__set_react_attribute(nm, varname)
            self.set_attribute("tp_updatevars", ";".join(name_list))
        return self

    def set_table_pagesize_options(self, default_size=[50, 100, 500]):
        page_size_options = self.__get_property("page_size_options", default_size)
        if isinstance(page_size_options, str):
            try:
                page_size_options = [int(s.strip()) for s in page_size_options.split(";")]
            except Exception as e:
                warnings.warn(f"page_size_options: invalid value {page_size_options}\n{e}")
        if isinstance(page_size_options, list):
            self.__set_json_attribute("pageSizeOptions", page_size_options)
        else:
            warnings.warn("page_size_options should be a list")
        return self

    def set_type(self, type_name: str):
        self.type_name = type_name
        self.set_attribute("type", type_name)
        return self

    def set_attributes(self, attributes: list[tuple]):
        def _get_val(attr, index, default_val):
            return attr[index] if len(attr) > index else default_val

        for attr in attributes:
            if not isinstance(attr, tuple):
                attr = (attr,)
            type = _get_val(attr, 1, AttributeType.string)
            if type == AttributeType.boolean:
                self.__set_boolean_attribute(attr[0], _get_val(attr, 2, False))
            elif type == AttributeType.string:
                self.__set_string_attribute(attr[0], _get_val(attr, 2, None), _get_val(attr, 3, True))
            elif type == AttributeType.react:
                self.__set_react_attribute(attr[0], _get_val(attr, 2, None))
            elif type == AttributeType.string_or_number:
                self.__set_string_or_number_attribute(attr[0], _get_val(attr, 2, None))
        return self

    def set_attribute(self, name, value):
        if name.startswith("on"):
            name = "tp_" + name
        self.el.set(name, value)
        return self

    def build(self):
        return self.el, self.m.start(0), self.m.end(0)

    def build_to_string(self):
        el_str = str(etree.tostring(self.el, encoding="utf8").decode("utf8"))
        el_str = el_str.replace("<?xml version='1.0' encoding='utf8'?>\n", "")
        el_str = el_str.replace("/>", ">")
        return el_str, self.element_name
