from operator import attrgetter
from markdown.util import etree
import pandas as pd
import json
import datetime

from .parse_attributes import parse_attributes
from ..utils import (
    _MapDictionary,
    dateToISO,
    get_client_var_name,
    getDataType,
    is_boolean_true,
)
from .utils import _add_to_dict_and_get, _get_columns_dict, _to_camel_case


class MarkdownBuilder:
    def __init__(
        self,
        m,
        el_element_name,
        default_value="<Empty>",
        has_attribute=False,
        attributes_val=3,
        allow_properties_config=True,
    ):
        self.m = m
        self.el_element_name = el_element_name
        self.value = default_value
        self.has_attribute = has_attribute
        # Allow property configuration by passing in dictionary
        self.allow_properties_config = allow_properties_config
        self.var_name = m.group(1)
        self.var_id = m.group(2)
        self.el = etree.Element(el_element_name)
        if has_attribute:
            self.attributes = parse_attributes(m.group(attributes_val)) or {}
            # Bind properties dictionary to attributes if condition is matched
            if allow_properties_config and "properties" in self.attributes:
                from ..gui import Gui

                properties_dict_name = self.attributes["properties"]
                Gui._get_instance().bind_var(properties_dict_name)
                properties_dict = getattr(Gui._get_instance(), properties_dict_name)
                if not isinstance(properties_dict, _MapDictionary):
                    raise Exception(
                        f"Can't find properties configuration dictionary for {str(m)}!"
                        f" Please review your GUI templates!"
                    )
                # Iterate through properties_dict and append to self.attributes
                for k, v in properties_dict.items():
                    self.attributes[k] = v
                    if isinstance(v, str):
                        # Bind potential function
                        Gui._get_instance().bind_func(v)

        if self.var_name:
            try:
                # Bind variable name (var_name string split in case
                # var_name is a dictionary)
                from ..gui import Gui

                Gui._get_instance().bind_var(self.var_name.split(sep=".")[0])
            except Exception:
                print(f"Couldn't bind variable '{self.var_name}'")

    def get_gui_value(self, fallback_value=None):
        if self.var_name:
            try:
                from ..gui import Gui

                self.value = attrgetter(self.var_name)(Gui._get_instance()._values)
            except Exception:
                print(f"WARNING: variable {self.var_name} doesn't exist")
                self.value = (
                    fallback_value
                    if fallback_value is not None
                    else "[Undefined: " + self.var_name + "]"
                )
        return self

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

    def set_varname(self):
        if self.var_name:
            self.set_attribute("key", self.var_name + "_" + str(self.var_id))
            self.set_attribute(
                "value",
                "{!" + get_client_var_name(self.var_name) + "!}",
            )
            self.set_attribute("tp_varname", self.var_name)
        return self

    def set_default_value(self):
        if self.el_element_name == "Input" and self.type_name == "button":
            self.set_attribute(
                "value",
                self.attributes["label"]
                if self.attributes and "label" in self.attributes
                else str(self.value),
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
            class_name + " " + Gui._get_instance()._config.style_config[config_class],
        )
        return self

    def set_withTime(self):
        if self.el_element_name != "DateSelector":
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
        if self.el_element_name != "Input" or self.type_name != "button":
            return self
        if self.attributes and "id" in self.attributes:
            self.set_attribute("id", self.attributes["id"])
            self.set_attribute("key", self.attributes["id"])
        elif self.var_name:
            self.set_attribute("id", self.var_name + "_" + str(self.var_id))
            self.set_attribute("key", self.var_name + "_" + str(self.var_id))
        if self.attributes and "on_action" in self.attributes:
            self.set_attribute("actionName", self.attributes["on_action"])
        else:
            self.set_attribute("actionName", "")
        return self

    def set_table_pagesize(self, default_size=100):
        if self.el_element_name != "Table":
            return self
        page_size = (
            self.attributes
            and "page_size" in self.attributes
            and self.attributes["page_size"]
        ) or default_size
        self.set_attribute("pageSize", "{!" + str(page_size) + "!}")
        return self

    def set_table_pagesize_options(self, default_size=[50, 100, 500]):
        if self.el_element_name != "Table":
            return self
        page_size_options = (
            self.attributes
            and "page_size_options" in self.attributes
            and self.attributes["page_size_options"]
        ) or default_size
        if isinstance(page_size_options, str):
            page_size_options = [int(s.strip()) for s in page_size_options.split(";")]
        self.set_attribute(
            "pageSizeOptions", "{!" + json.dumps(page_size_options) + "!}"
        )
        return self

    def set_allow_all_rows(self, default_value=False):
        if self.el_element_name != "Table":
            return self
        return self.__set_boolean_attribute("allow_all_rows", default_value)

    def set_format(self):
        format = (
            self.attributes
            and "format" in self.attributes
            and self.attributes["format"]
        )
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

        return self.__set_boolean_attribute(
            "propagate", Gui._get_instance()._config.app_config["propagate"]
        )

    def __set_list_of_(self, name):
        lof = self.attributes and name in self.attributes and self.attributes[name]
        if isinstance(lof, str):
            lof = {s.strip(): s for s in lof.split(";")}
        if not isinstance(lof, dict):
            print(
                f"Error: on component {self.el_element_name} parameter {name} should be a string or a dict"
            )
            return self
        return self.set_attribute(_to_camel_case(name), "{!" + str(lof) + "!}")

    def __set_boolean_attribute(self, name, default_value=False):
        boolattr = self.attributes[name] if hasattr(self, "attributes") and self.attributes and name in self.attributes else None
        if boolattr is None :
            boolattr = default_value
        if isinstance(boolattr, str):
            boolattr = is_boolean_true(boolattr)
        return self.set_attribute(
            _to_camel_case(name), "{!" + str(boolattr).lower() + "!}"
        )

    def set_attribute(self, name, value):
        self.el.set(name, value)
        return self

    def build(self):
        return self.el, self.m.start(0), self.m.end(0)
