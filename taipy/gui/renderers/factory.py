import re
import typing as t
from datetime import datetime

from ..types import AttributeType
from .builder import Builder


class Factory:

    DEFAULT_CONTROL = "text"

    __CONTROL_DEFAULT_PROP_NAME = {
        "button": "label",
        "chart": "data",
        "content": "value",
        "date_selector": "date",
        "dialog": "open",
        "expandable": "title",
        "file_download": "content",
        "file_selector": "content",
        "image": "content",
        "indicator": "display",
        "input": "value",
        "layout": "columns",
        "menu": "lov",
        "navbar": "value",
        "number": "value",
        "pane": "open",
        "part": "type",
        "selector": "value",
        "slider": "value",
        "status": "value",
        "table": "data",
        "text": "value",
        "toggle": "value",
        "tree": "value",
    }

    __TEXT_ANCHORS = ["bottom", "top", "left", "right"]
    __TEXT_ANCHOR_NONE = "none"

    CONTROL_BUILDERS = {
        "button": lambda control_type, attrs: Builder(
            control_type=control_type,
            element_name="Button",
            attributes=attrs,
        )
        .set_value_and_default(with_update=False)
        .set_attributes(
            [
                ("id",),
                ("on_action", AttributeType.string, ""),
                ("active", AttributeType.dynamic_boolean, True),
            ]
        ),
        "chart": lambda control_type, attrs: Builder(
            control_type=control_type,
            element_name="Chart",
            attributes=attrs,
        )
        .set_value_and_default(with_default=False)
        .set_attributes(
            [
                ("id",),
                ("title",),
                ("width", AttributeType.string_or_number, "100vw"),
                ("height", AttributeType.string_or_number, "100vh"),
                ("layout", AttributeType.dict),
                ("range_change",),
                ("active", AttributeType.dynamic_boolean, True),
                ("limit_rows", AttributeType.boolean),
            ]
        )
        .get_chart_config("scatter", "lines+markers")
        .set_propagate()
        .set_refresh_on_update()
        .set_refresh(),
        "content": lambda control_type, attrs: Builder(
            control_type=control_type, element_name="PageContent", attributes=attrs
        ),
        "date_selector": lambda control_type, attrs: Builder(
            control_type=control_type,
            element_name="DateSelector",
            attributes=attrs,
            default_value=datetime.fromtimestamp(0),
        )
        .set_value_and_default()
        .set_attributes(
            [
                ("with_time", AttributeType.boolean),
                ("id",),
                ("active", AttributeType.dynamic_boolean, True),
            ]
        )
        .set_propagate(),
        "dialog": lambda control_type, attrs: Builder(
            control_type=control_type,
            element_name="Dialog",
            attributes=attrs,
        )
        .set_value_and_default(native_type=True)
        .set_attributes(
            [
                ("id",),
                ("title",),
                ("cancel_action",),
                ("cancel_label", AttributeType.string, "Cancel"),
                ("validate_action", AttributeType.string, "validate"),
                ("validate_label", AttributeType.string, "Validate"),
                ("active", AttributeType.dynamic_boolean, True),
                ("width", AttributeType.string_or_number),
                ("height", AttributeType.string_or_number),
            ]
        )
        .set_propagate()
        .set_partial()  # partial should be set before page_id
        .set_page_id(),
        "expandable": lambda control_type, attrs: Builder(
            control_type=control_type, element_name="Expandable", attributes=attrs, default_value=""
        )
        .set_value_and_default()
        .set_attributes(
            [
                ("id",),
                ("expanded", AttributeType.dynamic_boolean, True),
            ]
        ),
        "file_download": lambda control_type, attrs: Builder(
            control_type=control_type,
            element_name="FileDownload",
            attributes=attrs,
        )
        .set_value_and_default(var_name="label", with_update=False)
        .set_content("content", image=False)
        .set_attributes(
            [
                ("id",),
                ("on_action", AttributeType.string),
                ("active", AttributeType.dynamic_boolean, True),
                ("render", AttributeType.dynamic_boolean, True),
                ("auto", AttributeType.boolean, False),
                ("bypass_preview", AttributeType.boolean, True),
                ("name",),
            ]
        ),
        "file_selector": lambda control_type, attrs: Builder(
            control_type=control_type,
            element_name="FileSelector",
            attributes=attrs,
        )
        .set_value_and_default(var_name="label", with_update=False)
        .set_file_content()
        .set_attributes(
            [
                ("id",),
                ("on_action", AttributeType.string),
                ("active", AttributeType.dynamic_boolean, True),
                ("multiple", AttributeType.boolean, False),
                ("extensions",),
                ("drop_message",),
            ]
        ),
        "image": lambda control_type, attrs: Builder(
            control_type=control_type,
            element_name="Image",
            attributes=attrs,
        )
        .set_value_and_default(var_name="label", with_update=False)
        .set_content("content")
        .set_attributes(
            [
                ("id",),
                ("on_action", AttributeType.string, ""),
                ("active", AttributeType.dynamic_boolean, True),
                ("width",),
                ("height",),
            ]
        ),
        "indicator": lambda control_type, attrs: Builder(
            control_type=control_type,
            element_name="Indicator",
            attributes=attrs,
        )
        .set_value_and_default(with_update=False, native_type=True)
        .set_attributes(
            [
                ("id",),
                ("min", AttributeType.number),
                ("max", AttributeType.number),
                ("value", AttributeType.dynamic_number),
                ("format",),
            ]
        ),
        "input": lambda control_type, attrs: Builder(
            control_type=control_type,
            element_name="Input",
            attributes=attrs,
        )
        .set_type("text")
        .set_value_and_default()
        .set_propagate()
        .set_attributes(
            [
                ("id",),
                ("active", AttributeType.dynamic_boolean, True),
            ]
        ),
        "layout": lambda control_type, attrs: Builder(
            control_type=control_type, element_name="Layout", attributes=attrs, default_value=""
        )
        .set_value_and_default(with_default=False)
        .set_attributes(
            [
                ("id",),
                ("columns[mobile]",),
                ("gap",),
            ]
        ),
        "menu": lambda control_type, attrs: Builder(
            control_type=control_type,
            element_name="MenuCtl",
            attributes=attrs,
        )
        .get_adapter("lov")  # need to be called before set_lov
        .set_lov()
        .set_attributes(
            [
                ("id",),
                ("active", AttributeType.dynamic_boolean, True),
                ("label"),
                ("width"),
                ("width[mobile]",),
                ("on_action", AttributeType.string, "on_menu_action"),
                ("inactive_ids", AttributeType.dynamic_list),
            ]
        )
        .set_refresh_on_update()
        .set_propagate(),
        "navbar": lambda control_type, attrs: Builder(
            control_type=control_type, element_name="NavBar", attributes=attrs, default_value=""
        )
        .get_adapter("lov", multi_selection=False)  # need to be called before set_lov
        .set_lov()
        .set_attributes(
            [
                ("id",),
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
        .set_propagate()
        .set_attributes(
            [
                ("id",),
                ("active", AttributeType.dynamic_boolean, True),
            ]
        ),
        "pane": lambda control_type, attrs: Builder(
            control_type=control_type, element_name="Pane", attributes=attrs, default_value=""
        )
        .set_value_and_default(native_type=True)
        .set_attributes(
            [
                ("id",),
                ("anchor", AttributeType.string, "left"),
                ("close_action",),
                ("persistent", AttributeType.boolean, False),
                ("active", AttributeType.dynamic_boolean, True),
                ("width", AttributeType.string_or_number, "30vw"),
                ("height", AttributeType.string_or_number, "30vh"),
            ]
        )
        .set_propagate()
        .set_partial()  # partial should be set before page_id
        .set_page_id(),
        "part": lambda control_type, attrs: Builder(
            control_type=control_type, element_name="Part", attributes=attrs, default_value=""
        ).set_attributes([("id",), ("render", AttributeType.dynamic_boolean, True)]),
        "selector": lambda control_type, attrs: Builder(
            control_type=control_type,
            element_name="Selector",
            attributes=attrs,
        )
        .set_value_and_default(with_default=False)
        .get_adapter("lov")  # need to be called before set_lov
        .set_lov()
        .set_attributes(
            [
                ("filter", AttributeType.boolean),
                ("multiple", AttributeType.boolean),
                ("dropdown", AttributeType.boolean, False),
                ("id",),
                ("active", AttributeType.dynamic_boolean, True),
                ("height", AttributeType.string_or_number),
                ("width", AttributeType.string_or_number),
            ]
        )
        .set_refresh_on_update()
        .set_propagate(),
        "slider": lambda control_type, attrs: Builder(
            control_type=control_type,
            element_name="Slider",
            attributes=attrs,
            default_value=0,
        )
        .set_value_and_default(native_type=True)
        .set_attributes(
            [
                ("min", AttributeType.number, 0),
                ("max", AttributeType.number, 100),
                ("id",),
                ("active", AttributeType.dynamic_boolean, True),
                ("width", AttributeType.string, "300px"),
                ("height"),
                ("orientation"),
            ]
        )
        .get_adapter("lov")  # need to be called before set_lov
        .set_lov()
        .set_labels()
        .set_string_with_check("text_anchor", Factory.__TEXT_ANCHORS + [Factory.__TEXT_ANCHOR_NONE], "bottom")
        .set_propagate(),
        "status": lambda control_type, attrs: Builder(
            control_type=control_type,
            element_name="Status",
            attributes=attrs,
        )
        .set_value_and_default(with_update=False)
        .set_propagate()
        .set_attributes(
            [("id",), ("active", AttributeType.dynamic_boolean, True), ("without_close", AttributeType.boolean, False)]
        ),
        "table": lambda control_type, attrs: Builder(
            control_type=control_type,
            element_name="Table",
            attributes=attrs,
        )
        .set_value_and_default(with_default=False)
        .get_dataframe_attributes()
        .set_attributes(
            [
                ("page_size", AttributeType.react, 100),
                ("allow_all_rows", AttributeType.boolean),
                ("show_all", AttributeType.boolean),
                ("auto_loading", AttributeType.boolean),
                ("width", AttributeType.string_or_number, "100vw"),
                ("height", AttributeType.string_or_number, "80vh"),
                ("id",),
                ("active", AttributeType.dynamic_boolean, True),
                ("editable", AttributeType.dynamic_boolean, True),
                ("edit_action",),
                ("delete_action",),
                ("add_action",),
                ("nan_value",),
            ]
        )
        .set_refresh()
        .set_propagate()
        .get_list_attribute("selected", AttributeType.number)
        .set_refresh_on_update()
        .set_table_pagesize_options(),
        "text": lambda control_type, attrs: Builder(
            control_type=control_type,
            element_name="Field",
            attributes=attrs,
        )
        .set_value_and_default(with_update=False)
        .set_dataType()
        .set_attributes(
            [
                ("format",),
                ("id",),
            ]
        ),
        "toggle": lambda control_type, attrs: Builder(
            control_type=control_type, element_name="Toggle", attributes=attrs, default_value=""
        )
        .set_value_and_default(with_default=False)
        .get_adapter("lov", multi_selection=False)  # need to be called before set_lov
        .set_lov()
        .set_attributes(
            [
                ("id",),
                ("label",),
                ("active", AttributeType.dynamic_boolean, True),
                ("unselected_value", AttributeType.string, ""),
            ]
        )
        .set_kind()
        .set_refresh_on_update()
        .set_propagate(),
        "tree": lambda control_type, attrs: Builder(
            control_type=control_type,
            element_name="TreeView",
            attributes=attrs,
        )
        .set_value_and_default(with_default=False)
        .get_adapter("lov")  # need to be called before set_lov
        .set_lov()
        .set_attributes(
            [
                ("filter", AttributeType.boolean),
                ("multiple", AttributeType.boolean),
                ("id",),
                ("active", AttributeType.dynamic_boolean, True),
                ("height", AttributeType.string_or_number),
                ("width", AttributeType.string_or_number),
            ]
        )
        .set_refresh_on_update()
        .set_propagate(),
    }

    # TODO: process \" in property value
    _PROPERTY_RE = re.compile(r"\s+([a-zA-Z][\.a-zA-Z_$0-9]*(?:\[(?:.*?)\])?)=\"((?:(?:(?<=\\)\")|[^\"])*)\"")

    @staticmethod
    def get_default_property_name(control_name: str) -> t.Optional[str]:
        return Factory.__CONTROL_DEFAULT_PROP_NAME.get(control_name.split(".", 1)[0])
