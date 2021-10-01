import re
from datetime import datetime

from .builder import Builder


class Factory:

    CONTROL_DEFAULT_PROP_NAME = {
        "field": "value",
        "button": "label",
        "input": "value",
        "number": "value",
        "date_selector": "date",
        "slider": "value",
        "selector": "value",
        "table": "data",
    }

    CONTROL_BUILDERS = {
        "field": lambda control_type, attrs: Builder(
            control_type=control_type,
            element_name="Field",
            attributes=attrs,
            default_value="<empty>",
        )
        .get_gui_value()
        .set_varname()
        .set_default_value()
        .set_className(class_name="taipy-field", config_class="field")
        .set_dataType()
        .set_format(),
        "button": lambda control_type, attrs: Builder(
            control_type=control_type,
            element_name="Input",
            attributes=attrs,
            default_value="<empty>",
        )
        .set_type("button")
        .get_gui_value()
        .set_varname()
        .set_default_value()
        .set_className(class_name="taipy-button", config_class="button")
        .set_button_attribute(),
        "input": lambda control_type, attrs: Builder(
            control_type=control_type,
            element_name="Input",
            attributes=attrs,
            default_value="<empty>",
        )
        .set_type("text")
        .get_gui_value()
        .set_varname()
        .set_default_value()
        .set_propagate()
        .set_className(class_name="taipy-input", config_class="input"),
        "number": lambda control_type, attrs: Builder(
            control_type=control_type,
            element_name="Input",
            attributes=attrs,
            default_value=0,
        )
        .set_type("number")
        .get_gui_value(fallback_value=0)
        .set_varname()
        .set_default_value()
        .set_className(class_name="taipy-number", config_class="input")
        .set_propagate(),
        "date_selector": lambda control_type, attrs: Builder(
            control_type=control_type,
            element_name="DateSelector",
            attributes=attrs,
            default_value="",
        )
        .get_gui_value(fallback_value=datetime.fromtimestamp(0))
        .set_varname()
        .set_default_value()
        .set_className(class_name="taipy-date-selector", config_class="date_selector")
        .set_withTime()
        .set_propagate(),
        "slider": lambda control_type, attrs: Builder(
            control_type=control_type,
            element_name="Input",
            attributes=attrs,
            default_value=0,
        )
        .set_type("range")
        .get_gui_value(fallback_value=0)
        .set_varname()
        .set_default_value()
        .set_className(class_name="taipy-slider", config_class="slider")
        .set_attribute("min", "1")
        .set_attribute("max", "100")
        .set_propagate(),
        "selector": lambda control_type, attrs: Builder(
            control_type=control_type,
            element_name="Selector",
            attributes=attrs,
        )
        .set_varname()
        .set_className(class_name="taipy-selector", config_class="selector")
        .get_gui_value()
        .set_lov()
        .set_filter()
        .set_multiple()
        .set_default_value()
        .set_propagate(),
        "table": lambda control_type, attrs: Builder(
            control_type=control_type,
            element_name="Table",
            attributes=attrs,
        )
        .set_varname()
        .set_className(class_name="taipy-table", config_class="table")
        .get_gui_value()
        .get_dataframe_attributes()
        .set_table_pagesize()
        .set_table_pagesize_options()
        .set_allow_all_rows(),
    }

    _PROPERTY_RE = re.compile(r"([a-zA-Z][\.a-zA-Z_$0-9]*)\s*(?:=(.*))?")
    # Same as Preprocessor._SPLIT_RE. TODO: share or move to utils?
    _SPLIT_RE = re.compile(r"(?<!\\\\)\|")

    @staticmethod
    def create(control_type: str, properties_fragment: str) -> str:
        # Create properties dict from properties_fragment
        attributes = {}
        for property in Factory._SPLIT_RE.split(properties_fragment):
            prop_match = Factory._PROPERTY_RE.match(property)
            if prop_match:
                attributes[prop_match.group(1)] = prop_match.group(2)
            else:
                raise ValueError(f"Invalid property syntax: '{property}'")
        builder = Factory.CONTROL_BUILDERS[control_type](control_type, attributes)
        if builder:
            return builder.el
        else:
            return f"<|INVALID SYNTAX - Control is '{control_type}'|>"

    @staticmethod
    def get_default_property_name(control_name: str) -> str:
        return Factory.CONTROL_DEFAULT_PROP_NAME.get(control_name)
