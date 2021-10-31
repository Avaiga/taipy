import re
import typing as t
from datetime import datetime

from ..wstype import AttributeType
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
        "chart": "data",
        "status": "value",
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
        .set_attributes([("format"), ("id")]),
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
        .set_attributes([("id"), ("on_action", AttributeType.string, "")]),
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
        .set_className(class_name="taipy-input", config_class="input")
        .set_attributes([("id")]),
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
        .set_propagate()
        .set_attributes([("id")]),
        "date_selector": lambda control_type, attrs: Builder(
            control_type=control_type,
            element_name="DateSelector",
            attributes=attrs,
            default_value=datetime.fromtimestamp(0),
        )
        .set_expresion_hash()
        .set_default_value()
        .set_className(class_name="taipy-date-selector", config_class="date_selector")
        .set_attributes([("with_time", AttributeType.boolean), ("id")])
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
        .set_attributes([("min", AttributeType.string, "1"), ("max", AttributeType.string, "100"), ("id")])
        .set_propagate(),
        "selector": lambda control_type, attrs: Builder(
            control_type=control_type,
            element_name="Selector",
            attributes=attrs,
        )
        .set_expresion_hash()
        .set_className(class_name="taipy-selector", config_class="selector")
        .get_adapter("lov")  # need to be called before set_lov
        .set_lov()
        .set_attributes([("filter", AttributeType.boolean), ("multiple", AttributeType.boolean), ("id")])
        .set_refresh_on_update()
        .set_propagate(),
        "table": lambda control_type, attrs: Builder(
            control_type=control_type,
            element_name="Table",
            attributes=attrs,
        )
        .set_expresion_hash()
        .set_className(class_name="taipy-table", config_class="table")
        .get_dataframe_attributes()
        .set_attributes(
            [
                ("page_size", AttributeType.react, 100),
                ("allow_all_rows", AttributeType.boolean),
                ("show_all", AttributeType.boolean),
                ("auto_loading", AttributeType.boolean),
                ("width", AttributeType.string_or_number, "100vw"),
                ("height", AttributeType.string_or_number, "100vh"),
                ("id"),
            ]
        )
        .set_refresh()
        .set_propagate()
        .get_list_attribute("selected", AttributeType.number)
        .set_refresh_on_update()
        .set_table_pagesize_options(),
        "dialog": lambda control_type, attrs: Builder(
            control_type=control_type,
            element_name="Dialog",
            attributes=attrs,
        )
        .set_expresion_hash()
        .set_className(class_name="taipy-dialog", config_class="dialog")
        .set_attributes(
            [
                ("id"),
                ("title"),
                ("cancel_action"),
                ("cancel_label", AttributeType.string, "Cancel"),
                ("validate_action", AttributeType.string, "validate"),
                ("validate_label", AttributeType.string, "Validate"),
                ("open", AttributeType.boolean),
            ]
        )
        .set_default_value()
        .set_propagate()
        .set_partial()  # partial should be set before page_id
        .set_page_id(),
        "chart": lambda control_type, attrs: Builder(
            control_type=control_type,
            element_name="Chart",
            attributes=attrs,
        )
        .set_expresion_hash()
        .set_className(class_name="taipy-chart", config_class="chart")
        .set_attributes(
            [
                ("id"),
                ("title"),
                ("width", AttributeType.string_or_number, "100vw"),
                ("height", AttributeType.string_or_number, "100vh"),
                ("layout", AttributeType.dict),
                ("range_change"),
            ]
        )
        .get_chart_config("scatter", "lines+markers")
        .set_propagate()
        .set_refresh_on_update()
        .set_refresh(),
        "status": lambda control_type, attrs: Builder(
            control_type=control_type,
            element_name="Status",
            attributes=attrs,
        )
        .set_expresion_hash()
        .set_default_value()
        .set_className(class_name="taipy-status", config_class="status")
        .set_propagate()
        .set_attributes(
            [
                ("id"),
            ]
        ),
    }

    # TODO: process \" in property value
    _PROPERTY_RE = re.compile(r"\s+([a-zA-Z][\.a-zA-Z_$0-9]*(?:\[(?:.*?)\])?)=\"((?:(?:(?<=\\)\")|[^\"])*)\"")

    @staticmethod
    def create_markdown_element(control_type: str, all_properties: str) -> str:
        # Create properties dict from all_properties
        property_pairs = Factory._PROPERTY_RE.findall(all_properties)
        properties = {property[0]: property[1] for property in property_pairs}
        builder = Factory.CONTROL_BUILDERS[control_type](control_type, properties)
        if builder:
            return builder.el
        else:
            return f"<|INVALID SYNTAX - Control is '{control_type}'|>"

    @staticmethod
    def create_html_element(control_type: str, all_properties: t.Dict[str, str]) -> t.Tuple[str, str]:
        builder = Factory.CONTROL_BUILDERS[control_type](control_type, all_properties)
        if not builder:
            return f"<div>INVALID SYNTAX - Control is '{control_type}'", "div"
        builder_str, element_name = builder.build_to_string()
        return builder_str, element_name

    @staticmethod
    def get_default_property_name(control_name: str) -> t.Optional[str]:
        return Factory.CONTROL_DEFAULT_PROP_NAME.get(control_name)
