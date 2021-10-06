import datetime
import json
import warnings
from operator import attrgetter

import pandas as pd
from markdown.util import etree

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
        from .factory import Factory
        from ..gui import Gui

        self.element_name = element_name
        self.attributes = attributes
        self.value = default_value
        self.el = etree.Element(element_name)
        self._gui = Gui._get_instance()
        # Whether this object has been evaluated (by expression) in preprocessor
        self.has_evaluated = False
        default_property_name = Factory.get_default_property_name(control_type)
        default_property_value = attributes.get(default_property_name)
        if default_property_value:
            self.has_evaluated = True
            if self._gui._is_expression(default_property_value):
                default_property_value = self._gui._fetch_expression_list(default_property_value)[0]
                self.value = attrgetter(default_property_value)(self._gui._values)
                self.expr_hash = default_property_value
                self.expr = self._gui._hash_to_expr[self.expr_hash]
            else:
                self.value = self.expr_hash = self.expr = default_property_value

        def parse_attribute_value(value):
            if v is not None and self._gui._is_expression(value):
                hash_value = self._gui._fetch_expression_list(value)[0]
                return attrgetter(hash_value)(self._gui._values)
            return value

        # Bind properties dictionary to attributes if condition is matched (will leave the binding for function at the builder )
        if "properties" in self.attributes:
            properties_dict_name = parse_attribute_value(self.attributes["properties"])
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
            v = parse_attribute_value(v)
            if isinstance(v, str):
                # Bind potential function
                self._gui.bind_func(v)
            # Try to evaluate as expressions
            if v is not None:
                self.attributes[k] = v

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

    def set_expresion_hash(self):
        if self.has_evaluated:
            self.set_attribute("key", self.expr_hash)
            self.set_attribute(
                "value",
                "{!" + self.expr_hash + "!}",
            )
            self.set_attribute("tp_varname", self.expr)
        return self

    def set_default_value(self):
        if self.element_name == "Input" and self.type_name == "button":
            self.set_attribute(
                "value",
                str(self.value)
                # self.attributes["label"] if self.attributes and "label" in self.attributes else str(self.value),
            )
        elif isinstance(self.value, datetime.datetime):
            self.set_attribute("defaultvalue", dateToISO(self.value))
        elif isinstance(self.value, str):
            self.set_attribute("defaultvalue", self.value)
        else:
            self.set_attribute("defaultvalue", "{!" + str(self.value) + "!}")
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

    def set_dataType(self):
        self.set_attribute("dataType", getDataType(self.value))
        return self

    def set_button_attribute(self):
        if self.element_name != "Input" or self.type_name != "button":
            return self
        if self.attributes and "id" in self.attributes:
            self.set_attribute("id", self.attributes["id"])
            self.set_attribute("key", self.attributes["id"])
        elif self.has_evaluated:
            self.set_attribute("id", self.expr_hash)
            self.set_attribute("key", self.expr_hash)
        if self.attributes and "on_action" in self.attributes:
            self.set_attribute("actionName", self.attributes["on_action"])
        else:
            self.set_attribute("actionName", "")
        return self

    def set_table_pagesize(self, default_size=100):
        if self.element_name != "Table":
            return self
        page_size = (
            self.attributes and "page_size" in self.attributes and self.attributes["page_size"]
        ) or default_size
        self.set_attribute("pageSize", "{!" + str(page_size) + "!}")
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
            self.set_attribute("pageSizeOptions", "{!" + json.dumps(page_size_options) + "!}")
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

    def __set_list_of_(self, name):
        lof = self.attributes and name in self.attributes and self.attributes[name]
        if isinstance(lof, str):
            lof = {s.strip(): s for s in lof.split(";")}
        if not isinstance(lof, dict):
            warnings.warn(f"Error: Property {name} of component {self.element_name} should be a string or a dict")
            return self
        return self.set_attribute(_to_camel_case(name), "{!" + str(lof) + "!}")

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
        return self.set_attribute(_to_camel_case(name), "{!" + str(boolattr).lower() + "!}")

    def set_attribute(self, name, value):
        self.el.set(name, value)
        return self

    def build(self):
        return self.el, self.m.start(0), self.m.end(0)
