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
        "dialog": "open",
    }

    CONTROL_BUILDERS = {
        "field": lambda control_type, attrs: Builder(
            control_type=control_type,
            element_name="Field",
            attributes=attrs,
            default_value="<empty>",
        )
        .set_expresion_hash()
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
        .set_expresion_hash()
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
        .set_expresion_hash()
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
        .set_expresion_hash()
        .set_default_value()
        .set_className(class_name="taipy-number", config_class="input")
        .set_propagate(),
        "date_selector": lambda control_type, attrs: Builder(
            control_type=control_type,
            element_name="DateSelector",
            attributes=attrs,
            default_value=datetime.fromtimestamp(0),
        )
        .set_expresion_hash()
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
        .set_expresion_hash()
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
        .set_default_value()
        .set_expresion_hash()
        .set_className(class_name="taipy-selector", config_class="selector")
        .get_lov_label_getter()  # need to be called before set_lov
        .set_lov()
        .set_filter()
        .set_multiple()
        .set_refresh_on_update("lov")
        .set_propagate(),
        "table": lambda control_type, attrs: Builder(
            control_type=control_type,
            element_name="Table",
            attributes=attrs,
        )
        .set_expresion_hash()
        .set_className(class_name="taipy-table", config_class="table")
        .get_dataframe_attributes()
        .set_refresh()
        .set_table_pagesize()
        .set_table_pagesize_options()
        .set_allow_all_rows()
        .set_show_all()
        .set_auto_loading()
        .set_show_all(),
        "dialog": lambda control_type, attrs: Builder(
            control_type=control_type,
            element_name="Dialog",
            attributes=attrs,
        )
        .set_expresion_hash()
        .set_id()
        .set_className(class_name="taipy-dialog", config_class="dialog")
        .set_title()
        .set_default_value()
        .set_cancel_action()
        .set_validate_action()
        .set_cancel_action_text()
        .set_validate_action_text()
        .set_partial()  # partial should be set before page_id
        .set_page_id(),
    }

    # TODO: process \" in property value
    _PROPERTY_RE = re.compile(r"\s+([a-zA-Z][\.a-zA-Z_$0-9]*)=\"((?:(?:(?<=\\)\")|[^\"])*)\"")

    @staticmethod
    def create(control_type: str, all_properties: str) -> str:
        # Create properties dict from all_properties
        property_pairs = Factory._PROPERTY_RE.findall(all_properties)
        properties = {property[0]: property[1] for property in property_pairs}
        builder = Factory.CONTROL_BUILDERS[control_type](control_type, properties)
        if builder:
            return builder.el
        else:
            return f"<|INVALID SYNTAX - Control is '{control_type}'|>"

    @staticmethod
    def get_default_property_name(control_name: str) -> str:
        return Factory.CONTROL_DEFAULT_PROP_NAME.get(control_name)
