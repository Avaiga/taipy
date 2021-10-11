import datetime
import json
import typing as t
import warnings
from operator import attrgetter
from types import FunctionType

import pandas as pd
from markdown.util import etree

from ..page import Partial
from ..utils import _MapDictionary, dateToISO, get_client_var_name, getDataType, is_boolean_true
from .utils import _add_to_dict_and_get, _get_columns_dict, _to_camel_case


class Builder:
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
        self.attributes = attributes
        self.__hashes = {}
        self.value = default_value
        self.el = etree.Element(element_name)
        self._gui = Gui._get_instance()
        # Whether this object has been evaluated (by expression) in preprocessor
        self.has_evaluated = False
        default_property_name = Factory.get_default_property_name(control_type)
        default_property_value = attributes.get(default_property_name)
        if default_property_value:
            self.has_evaluated = True
            if isinstance(default_property_value, str) and self._gui._is_expression(default_property_value):
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

    @staticmethod
    def __to_string(x: t.Any) -> str:
        return str(x)

    def __parse_attribute_value(self, value) -> t.Tuple:
        if isinstance(value, str) and self._gui._is_expression(value):
            hash_value = self._gui._fetch_expression_list(value)[0]
            self._gui.bind_var(hash_value)
            return (attrgetter(hash_value)(self._gui._values), hash_value)
        return (value, None)

    def __get_id_label(self, elt, getter, idx):
        ret = getter(elt)
        if isinstance(ret, (list, tuple)) and len(ret) >= 2:
            return ret
        elt_id = elt.id if hasattr(elt, "id") else None
        if not elt_id and isinstance(elt, dict) and "id" in elt:
            elt_id = elt["id"]
        if not elt_id:
            elt_id = idx
        return (elt_id, ret)

    def __get_list_of_(self, name):
        lof = self.attributes and name in self.attributes and self.attributes[name]
        if isinstance(lof, str):
            lof = {s.strip(): s for s in lof.split(";")}
        if isinstance(lof, _MapDictionary):
            lof = lof._dict
        return lof

    def __set_list_of_(self, name):
        lof = self.__get_list_of_(name)
        if not isinstance(lof, dict):
            warnings.warn(f"Component {self.element_name} Attribute {name}: should be a string or a dict")
            return self
        return self.__set_react_attribute(_to_camel_case(name), lof)

    def __set_react_attribute(self, name, value):
        return self.set_attribute(name, "{!" + (str(value).lower() if isinstance(value, bool) else str(value)) + "!}")

    def __set_string_attribute(
        self, name: str, default_value: t.Optional[str] = None, optional: t.Optional[bool] = True
    ):
        strattr = (
            self.attributes[name]
            if hasattr(self, "attributes") and self.attributes and name in self.attributes
            else default_value
        )
        if not strattr:
            if not optional:
                warnings.warn(f"property {name} is required for component {self.control_type}")
            return self
        return self.set_attribute(_to_camel_case(name), strattr)

    def __set_boolean_attribute(self, name, default_value=False):
        boolattr = (
            self.attributes[name]
            if hasattr(self, "attributes") and self.attributes and name in self.attributes
            else None
        )
        if boolattr is None:
            boolattr = default_value
        if isinstance(boolattr, str):
            boolattr = is_boolean_true(boolattr)
        return self.__set_react_attribute(_to_camel_case(name), boolattr)

    def get_dataframe_attributes(self, date_format="MM/dd/yyyy"):
        if isinstance(self.value, pd.DataFrame):
            attributes = self.attributes or {}
            columns = _get_columns_dict(
                self.value,
                _add_to_dict_and_get(attributes, "columns", {}),
                _add_to_dict_and_get(attributes, "date_format", date_format),
            )
            attributes["columns"] = columns
            self.set_attribute("columns", json.dumps(columns))
        return self

    def get_lov_label_getter(self):
        lov = self.__get_list_of_("lov")
        if isinstance(lov, list):
            lov_label_fn = self.attributes and "label_getter" in self.attributes and self.attributes["label_getter"]
            if not lov_label_fn:
                lov_label_fn = Builder.__to_string
            if not isinstance(lov_label_fn, FunctionType):
                warnings.warn("Component Selector Attribute ")
                lov_label_fn = Builder.__to_string
            ret_dict = {}
            for elt in lov:
                try:
                    ret = self.__get_id_label(elt, lov_label_fn, len(ret_dict))
                    ret_dict[str(ret[0])] = str(ret[1])
                except Exception as e:
                    warnings.warn(
                        f"Component {self.element_name} Attribute label_getter: function raised an exception {e}"
                    )
            self.attributes["lov"] = ret_dict
            if not isinstance(self.value, str):
                ret_list = []
                val_list = self.value if isinstance(self.value, list) else [self.value]
                for val in val_list:
                    if isinstance(val, str):
                        ret_list.append(val)
                    else:
                        try:
                            ret_list.append(str(self.__get_id_label(val, lov_label_fn, -1)[0]))
                        except Exception as e:
                            warnings.warn(
                                f"Component {self.element_name} Attribute label_getter: function raised an exception {e}"
                            )
                if len(ret_list) > 1:
                    self.__set_react_attribute("defaultvalue", ret_list)
                else:
                    self.set_attribute("defaultvalue", ret_list[0] if ret_list else "")
        return self

    def set_expresion_hash(self):
        if self.has_evaluated:
            self.set_attribute("key", self.expr_hash)
            self.__set_react_attribute(
                "value",
                get_client_var_name(self.expr_hash),
            )
            self.set_attribute("tp_varname", self.expr)
        return self

    def set_default_value(self):
        if isinstance(self.value, datetime.datetime):
            self.set_attribute("defaultvalue", dateToISO(self.value))
        elif isinstance(self.value, str):
            self.set_attribute("defaultvalue", self.value)
        else:
            self.__set_react_attribute("defaultvalue", self.value)
        return self

    def set_className(self, class_name="", config_class="input"):
        from ..gui import Gui

        self.set_attribute(
            "className",
            class_name + " " + self._gui._config.style_config[config_class],
        )
        return self

    def set_withTime(self):
        if self.element_name != "DateSelector":
            return self
        return self.__set_boolean_attribute("with_time")

    def set_type(self, type_name=None):
        self.type_name = type_name
        self.set_attribute("type", type_name)
        return self

    def set_partial(self):
        if self.element_name != "Dialog":
            return self
        if "partial" in self.attributes and self.attributes["partial"]:
            if "page_id" in self.attributes and self.attributes["page_id"]:
                warnings.warn("Dialog component: page_id and partial should not be defined at the same time")
            if isinstance(self.attributes["partial"], Partial):
                self.attributes["page_id"] = self.attributes["partial"].route
        return self

    def set_dataType(self):
        self.set_attribute("dataType", getDataType(self.value))
        return self

    def set_button_attribute(self):
        if self.element_name != "Input" or self.type_name != "button":
            return self
        self.set_id()
        if self.attributes and "id" in self.attributes:
            self.set_attribute("key", self.attributes["id"])
        elif self.has_evaluated:
            self.set_attribute("key", self.expr_hash)
        if self.attributes and "on_action" in self.attributes:
            self.set_attribute("actionName", self.attributes["on_action"])
        else:
            self.set_attribute("actionName", "")
        return self

    def set_id(self):
        if self.attributes and "id" in self.attributes:
            self.set_attribute("id", self.attributes["id"])
        elif self.has_evaluated:
            self.set_attribute("id", self.expr_hash)
        return self

    def set_table_pagesize(self, default_size=100):
        if self.element_name != "Table":
            return self
        page_size = (
            self.attributes and "page_size" in self.attributes and self.attributes["page_size"]
        ) or default_size
        self.__set_react_attribute("pageSize", page_size)
        return self

    def set_table_pagesize_options(self, default_size=[50, 100, 500]):
        if self.element_name != "Table":
            return self
        page_size_options = (
            self.attributes and "page_size_options" in self.attributes and self.attributes["page_size_options"]
        ) or default_size
        if isinstance(page_size_options, str):
            try:
                page_size_options = [int(s.strip()) for s in page_size_options.split(";")]
            except Exception as e:
                warnings.warn(f"page_size_options: invalid value {page_size_options}\n{e}")
        if isinstance(page_size_options, list):
            self.__set_react_attribute("pageSizeOptions", page_size_options)
        else:
            warnings.warn("page_size_options should be a list")
        return self

    def set_allow_all_rows(self, default_value=False):
        if self.element_name != "Table":
            return self
        return self.__set_boolean_attribute("allow_all_rows", default_value)

    def set_show_all(self, default_value=False):
        if self.element_name != "Table":
            return self
        return self.__set_boolean_attribute("show_all", default_value)

    def set_auto_loading(self, default_value=False):
        if self.element_name != "Table":
            return self
        return self.__set_boolean_attribute("auto_loading", default_value)

    def set_format(self):
        format = self.attributes and "format" in self.attributes and self.attributes["format"]
        if format:
            self.set_attribute("format", format)
        return self

    def set_filter(self, default_value=False):
        return self.__set_boolean_attribute("filter", default_value)

    def set_multiple(self, default_value=False):
        return self.__set_boolean_attribute("multiple", default_value)

    def set_lov(self):
        return self.__set_list_of_("lov")

    def set_propagate(self):
        from ..gui import Gui

        return self.__set_boolean_attribute("propagate", self._gui._config.app_config["propagate"])

    def set_refresh(self):
        return self.__set_react_attribute("refresh", get_client_var_name(self.expr_hash + ".refresh"))

    def set_title(self):
        return self.__set_string_attribute("title")

    def set_open(self):
        return self.__set_boolean_attribute("open")

    def set_refresh_on_update(self, name=None):
        if name:
            if not isinstance(name, (tuple, list)):
                name = [name]
            name_list = []
            for nm in name:
                varname = self.__hashes[nm] if nm in self.__hashes else None
                if varname:
                    name_list.append(varname)
                self.__set_react_attribute("tp_" + nm, varname)
            self.set_attribute("tp_updatevars", ";".join(name_list))
        return self

    def set_cancel_action(self):
        return self.__set_string_attribute("cancel_action")

    def set_validate_action(self):
        return self.__set_string_attribute("validate_action", "validate")

    def set_cancel_action_text(self):
        return self.__set_string_attribute("cancel_action_text", "Cancel")

    def set_validate_action_text(self):
        return self.__set_string_attribute("validate_action_text", "Validate")

    def set_page_id(self):
        return self.__set_string_attribute("page_id", optional=False)

    def set_attribute(self, name, value):
        self.el.set(name, value)
        return self

    def build(self):
        return self.el, self.m.start(0), self.m.end(0)
