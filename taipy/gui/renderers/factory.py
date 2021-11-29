import re
import typing as t
from datetime import datetime

from ..wstype import AttributeType
from .builder import Builder


class Factory:

    __CONTROL_DEFAULT_PROP_NAME = {
        "field": "value",
        "button": "label",
        "input": "value",
        "number": "value",
        "date_selector": "date",
        "slider": "value",
        "selector": "value",
        "tree": "value",
        "table": "data",
        "dialog": "open",
        "chart": "data",
        "status": "value",
        "toggle": "value",
        "content": "value",
        "navbar": "value",
        "layout": "columns",
        "part": "type",
        "expandable": "title",
    }

    CONTROL_BUILDERS = {
        "field": lambda control_type, attrs: Builder(
            control_type=control_type,
            element_name="Field",
            attributes=attrs,
            default_value="<empty>",
        )
        .set_value_and_default(False)
        .set_classNames(class_name="taipy-field", config_class="field")
        .set_dataType()
        .set_attributes(
            [
                ("format"),
                ("id"),
            ]
        ),
        "button": lambda control_type, attrs: Builder(
            control_type=control_type,
            element_name="Button",
            attributes=attrs,
            default_value="<empty>",
        )
        .set_value_and_default(False)
        .set_classNames(class_name="taipy-button", config_class="button")
        .set_attributes(
            [
                ("id"),
                ("on_action", AttributeType.string, ""),
                ("active", AttributeType.dynamic_boolean, True),
            ]
        ),
        "input": lambda control_type, attrs: Builder(
            control_type=control_type,
            element_name="Input",
            attributes=attrs,
            default_value="<empty>",
        )
        .set_type("text")
        .set_value_and_default()
        .set_propagate()
        .set_classNames(class_name="taipy-input", config_class="input")
        .set_attributes(
            [
                ("id"),
                ("active", AttributeType.dynamic_boolean, True),
            ]
        ),
        "number": lambda control_type, attrs: Builder(
            control_type=control_type,
            element_name="Input",
            attributes=attrs,
            default_value=0,
        )
        .set_type("number")
        .set_value_and_default()
        .set_classNames(class_name="taipy-number", config_class="input")
        .set_propagate()
        .set_attributes(
            [
                ("id"),
                ("active", AttributeType.dynamic_boolean, True),
            ]
        ),
        "date_selector": lambda control_type, attrs: Builder(
            control_type=control_type,
            element_name="DateSelector",
            attributes=attrs,
            default_value=datetime.fromtimestamp(0),
        )
        .set_value_and_default()
        .set_classNames(class_name="taipy-date-selector", config_class="date_selector")
        .set_attributes(
            [
                ("with_time", AttributeType.boolean),
                ("id"),
                ("active", AttributeType.dynamic_boolean, True),
            ]
        )
        .set_propagate(),
        "slider": lambda control_type, attrs: Builder(
            control_type=control_type,
            element_name="Slider",
            attributes=attrs,
            default_value=0,
        )
        .set_value_and_default()
        .set_classNames(class_name="taipy-slider", config_class="slider")
        .set_attributes(
            [
                ("min", AttributeType.number, 0),
                ("max", AttributeType.number, 100),
                ("id"),
                ("active", AttributeType.dynamic_boolean, True),
                ("width", AttributeType.string_or_number, 200),
            ]
        )
        .set_propagate(),
        "selector": lambda control_type, attrs: Builder(
            control_type=control_type,
            element_name="Selector",
            attributes=attrs,
        )
        .set_value_and_default(with_default=False)
        .set_classNames(class_name="taipy-selector", config_class="selector")
        .get_adapter("lov")  # need to be called before set_lov
        .set_lov()
        .set_attributes(
            [
                ("filter", AttributeType.boolean),
                ("multiple", AttributeType.boolean),
                ("id"),
                ("active", AttributeType.dynamic_boolean, True),
                ("height", AttributeType.string_or_number),
                ("width", AttributeType.string_or_number),
            ]
        )
        .set_refresh_on_update()
        .set_propagate(),
        "tree": lambda control_type, attrs: Builder(
            control_type=control_type,
            element_name="TreeView",
            attributes=attrs,
        )
        .set_value_and_default(with_default=False)
        .set_classNames(class_name="taipy-tree", config_class="tree")
        .get_adapter("lov")  # need to be called before set_lov
        .set_lov()
        .set_attributes(
            [
                ("filter", AttributeType.boolean),
                ("multiple", AttributeType.boolean),
                ("id"),
                ("active", AttributeType.dynamic_boolean, True),
                ("height", AttributeType.string_or_number),
                ("width", AttributeType.string_or_number),
            ]
        )
        .set_refresh_on_update()
        .set_propagate(),
        "table": lambda control_type, attrs: Builder(
            control_type=control_type,
            element_name="Table",
            attributes=attrs,
        )
        .set_value_and_default(with_default=False)
        .set_classNames(class_name="taipy-table", config_class="table")
        .get_dataframe_attributes()
        .set_attributes(
            [
                ("page_size", AttributeType.react, 100),
                ("allow_all_rows", AttributeType.boolean),
                ("show_all", AttributeType.boolean),
                ("auto_loading", AttributeType.boolean),
                ("width", AttributeType.string_or_number, "100vw"),
                ("height", AttributeType.string_or_number, "80vh"),
                ("id"),
                ("active", AttributeType.dynamic_boolean, True),
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
        .set_value_and_default()
        .set_classNames(class_name="taipy-dialog", config_class="dialog")
        .set_attributes(
            [
                ("id"),
                ("title"),
                ("cancel_action"),
                ("cancel_label", AttributeType.string, "Cancel"),
                ("validate_action", AttributeType.string, "validate"),
                ("validate_label", AttributeType.string, "Validate"),
                ("open", AttributeType.boolean),
                ("active", AttributeType.dynamic_boolean, True),
            ]
        )
        .set_propagate()
        .set_partial()  # partial should be set before page_id
        .set_page_id(),
        "chart": lambda control_type, attrs: Builder(
            control_type=control_type,
            element_name="Chart",
            attributes=attrs,
        )
        .set_value_and_default(with_default=False)
        .set_classNames(class_name="taipy-chart", config_class="chart")
        .set_attributes(
            [
                ("id"),
                ("title"),
                ("width", AttributeType.string_or_number, "100vw"),
                ("height", AttributeType.string_or_number, "100vh"),
                ("layout", AttributeType.dict),
                ("range_change"),
                ("active", AttributeType.dynamic_boolean, True),
                ("limit_rows", AttributeType.boolean),
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
        .set_value_and_default(False)
        .set_classNames(class_name="taipy-status", config_class="status")
        .set_propagate()
        .set_attributes(
            [("id"), ("active", AttributeType.dynamic_boolean, True), ("without_close", AttributeType.boolean, False)]
        ),
        "toggle": lambda control_type, attrs: Builder(
            control_type=control_type, element_name="Toggle", attributes=attrs, default_value=""
        )
        .set_value_and_default(with_default=False)
        .set_classNames(class_name="taipy-toggle", config_class="toggle")
        .get_adapter("lov", False)  # need to be called before set_lov
        .set_lov()
        .set_attributes(
            [
                ("id"),
                ("label"),
                ("active", AttributeType.dynamic_boolean, True),
                ("unselected_value", AttributeType.string, ""),
            ]
        )
        .set_kind()
        .set_refresh_on_update()
        .set_propagate(),
        "content": lambda control_type, attrs: Builder(
            control_type=control_type, element_name="PageContent", attributes=attrs
        ),
        "navbar": lambda control_type, attrs: Builder(
            control_type=control_type, element_name="NavBar", attributes=attrs, default_value=""
        )
        .set_classNames(class_name="taipy-navbar", config_class="navbar")
        .get_adapter("lov", False)  # need to be called before set_lov
        .set_lov()
        .set_attributes(
            [
                ("id"),
                ("active", AttributeType.dynamic_boolean, True),
            ]
        ),
        "layout": lambda control_type, attrs: Builder(
            control_type=control_type, element_name="Layout", attributes=attrs, default_value=""
        )
        .set_classNames(class_name="taipy-layout", config_class="layout")
        .set_attributes(
            [
                ("id"),
                ("columns"),
                ("columns[mobile]"),
                ("gap"),
            ]
        ),
        "part": lambda control_type, attrs: Builder(
            control_type=control_type, element_name="Part", attributes=attrs, default_value=""
        )
        .set_classNames(class_name="taipy-part", config_class="part")
        .set_attributes([("id"), ("render", AttributeType.dynamic_boolean, True)]),
        "expandable": lambda control_type, attrs: Builder(
            control_type=control_type, element_name="Expandable", attributes=attrs, default_value=""
        )
        .set_value_and_default()
        .set_classNames(class_name="taipy-expandable", config_class="expandable")
        .set_attributes(
            [
                ("id"),
                ("expanded", AttributeType.dynamic_boolean, True),
            ]
        ),
    }

    # TODO: process \" in property value
    _PROPERTY_RE = re.compile(r"\s+([a-zA-Z][\.a-zA-Z_$0-9]*(?:\[(?:.*?)\])?)=\"((?:(?:(?<=\\)\")|[^\"])*)\"")

    @staticmethod
    def get_default_property_name(control_name: str) -> t.Optional[str]:
        return Factory.__CONTROL_DEFAULT_PROP_NAME.get(control_name.split(".", 1)[0])
