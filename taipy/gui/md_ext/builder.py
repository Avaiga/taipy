from markdown.util import etree
from operator import attrgetter
from .parse_attributes import parse_attributes
from ..utils import is_boolean_true, dateToISO, getDataType, get_client_var_name, MapDictionary
from ..app import App


class MarkdownBuilder:
    def __init__(
        self,
        m,
        el_element_name,
        default_value="<Empty>",
        has_attribute=False,
        attributes_val=3,
        allow_properties_config=False,
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
            # bind properties dicitonary to attributes if condition is matched
            if allow_properties_config and "properties" in self.attributes:
                properties_dict_name = self.attributes["properties"]
                App._get_instance().bind_var(properties_dict_name)
                properties_dict = getattr(App._get_instance(), properties_dict_name)
                if not isinstance(properties_dict, MapDictionary):
                    raise Exception(f"Can't find properties configuration dictionary for {str(m)}! Please review your app templates!")
                # Interate through properties_dict and append to self.attributes
                for k, v in properties_dict._dict.items():
                    self.attributes[k] = v
        if self.var_name:
            try:
                # Bind variable name (var_name string split in case var_name is a dictionary)
                App._get_instance().bind_var(self.var_name.split(sep=".")[0])
            except:
                print("error")

    def get_app_value(self, fallback_value=None):
        if self.var_name:
            try:
                self.value = attrgetter(self.var_name)(App._get_instance()._values)
            except:
                print("Error getting app value of " + self.var_name)
                self.value = (
                    fallback_value
                    if fallback_value is not None
                    else "[Undefined: " + self.var_name + "]"
                )
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
        if self.el_element_name == "DateSelector":
            self.set_attribute("defaultvalue", dateToISO(self.value))
        if self.el_element_name == "Input" and self.type_name == "button":
            self.set_attribute(
                "value",
                self.attributes["label"]
                if self.attributes and "label" in self.attributes
                else str(self.value),
            )
        else:
            self.set_attribute("defaultvalue", str(self.value))
        return self

    def set_className(self, class_name="", config_class="input"):
        self.set_attribute(
            "className",
            class_name + " " + App._get_instance()._config.style_config[config_class],
        )
        return self

    def set_withTime(self):
        if self.el_element_name != "DateSelector":
            return self
        if (
            self.attributes
            and "with_time" in self.attributes
            and is_boolean_true(self.attributes["with_time"])
        ):
            self.set_attribute("withTime", str(True))
        return self

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
        self.set_attribute("pageSize", "{!" + page_size + "!}")
        return self

    def set_attribute(self, name, value):
        self.el.set(name, value)
        return self

    def build(self):
        return self.el, self.m.start(0), self.m.end(0)
