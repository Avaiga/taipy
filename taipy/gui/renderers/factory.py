import re
import typing as t
from datetime import datetime

from ..types import _AttributeType
from .builder import _Builder


class _Factory:

    DEFAULT_CONTROL = "text"

    __CONTROL_DEFAULT_PROP_NAME = {
        "button": "label",
        "chart": "data",
        "content": "value",
        "date": "date",
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
        "part": "render",
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
        "button": lambda gui, control_type, attrs: _Builder(
            gui=gui,
            control_type=control_type,
            element_name="Button",
            attributes=attrs,
        )
        .set_value_and_default(with_update=False)
        .set_attributes(
            [
                ("id",),
                ("on_action", _AttributeType.function, ""),
                ("active", _AttributeType.dynamic_boolean, True),
                ("hover_text", _AttributeType.dynamic_string),
            ]
        ),
        "chart": lambda gui, control_type, attrs: _Builder(
            gui=gui,
            control_type=control_type,
            element_name="Chart",
            attributes=attrs,
        )
        .set_value_and_default(with_default=False, var_type=_AttributeType.data)
        .set_attributes(
            [
                ("id",),
                ("title",),
                ("width", _AttributeType.string_or_number),
                ("height", _AttributeType.string_or_number),
                ("layout", _AttributeType.dict),
                ("plot_config", _AttributeType.dict),
                ("on_range_change", _AttributeType.function),
                ("active", _AttributeType.dynamic_boolean, True),
                ("limit_rows", _AttributeType.boolean),
                ("render", _AttributeType.dynamic_boolean, True),
                ("hover_text", _AttributeType.dynamic_string),
            ]
        )
        .get_chart_config("scatter", "lines+markers")
        .set_propagate()
        .set_refresh_on_update()
        .set_refresh(),
        "content": lambda gui, control_type, attrs: _Builder(
            gui=gui, control_type=control_type, element_name="PageContent", attributes=attrs
        ),
        "date": lambda gui, control_type, attrs: _Builder(
            gui=gui,
            control_type=control_type,
            element_name="DateSelector",
            attributes=attrs,
            default_value=datetime.fromtimestamp(0),
        )
        .set_value_and_default(var_type=_AttributeType.date)
        .set_attributes(
            [
                ("with_time", _AttributeType.boolean),
                ("id",),
                ("active", _AttributeType.dynamic_boolean, True),
                ("editable", _AttributeType.dynamic_boolean, True),
                ("hover_text", _AttributeType.dynamic_string),
            ]
        )
        .set_propagate(),
        "dialog": lambda gui, control_type, attrs: _Builder(
            gui=gui,
            control_type=control_type,
            element_name="Dialog",
            attributes=attrs,
        )
        .set_value_and_default(var_type=_AttributeType.dynamic_boolean)
        .set_partial()  # partial should be set before page
        .set_attributes(
            [
                ("id",),
                ("page",),
                ("title",),
                ("on_cancel", _AttributeType.function),
                ("cancel_label", _AttributeType.string, "Cancel"),
                ("on_validate", _AttributeType.function, "validate"),
                ("validate_label", _AttributeType.string, "Validate"),
                ("active", _AttributeType.dynamic_boolean, True),
                ("width", _AttributeType.string_or_number),
                ("height", _AttributeType.string_or_number),
                ("hover_text", _AttributeType.dynamic_string),
            ]
        )
        .set_propagate(),
        "expandable": lambda gui, control_type, attrs: _Builder(
            gui=gui, control_type=control_type, element_name="Expandable", attributes=attrs, default_value=None
        )
        .set_value_and_default()
        .set_partial()  # partial should be set before page
        .set_attributes(
            [
                ("id",),
                ("page",),
                ("expanded", _AttributeType.dynamic_boolean, True),
                ("hover_text", _AttributeType.dynamic_string),
            ]
        ),
        "file_download": lambda gui, control_type, attrs: _Builder(
            gui=gui,
            control_type=control_type,
            element_name="FileDownload",
            attributes=attrs,
        )
        .set_value_and_default(var_name="label", with_update=False)
        .set_content("content", image=False)
        .set_attributes(
            [
                ("id",),
                ("on_action", _AttributeType.function),
                ("active", _AttributeType.dynamic_boolean, True),
                ("render", _AttributeType.dynamic_boolean, True),
                ("auto", _AttributeType.boolean, False),
                ("bypass_preview", _AttributeType.boolean, True),
                ("name",),
                ("hover_text", _AttributeType.dynamic_string),
            ]
        ),
        "file_selector": lambda gui, control_type, attrs: _Builder(
            gui=gui,
            control_type=control_type,
            element_name="FileSelector",
            attributes=attrs,
        )
        .set_value_and_default(var_name="label", with_update=False)
        .set_file_content()
        .set_attributes(
            [
                ("id",),
                ("on_action", _AttributeType.function),
                ("active", _AttributeType.dynamic_boolean, True),
                ("multiple", _AttributeType.boolean, False),
                ("extensions",),
                ("drop_message",),
                ("hover_text", _AttributeType.dynamic_string),
            ]
        ),
        "image": lambda gui, control_type, attrs: _Builder(
            gui=gui,
            control_type=control_type,
            element_name="Image",
            attributes=attrs,
        )
        .set_value_and_default(var_name="label", with_update=False)
        .set_content("content")
        .set_attributes(
            [
                ("id",),
                ("on_action", _AttributeType.function, ""),
                ("active", _AttributeType.dynamic_boolean, True),
                ("width",),
                ("height",),
                ("hover_text", _AttributeType.dynamic_string),
            ]
        ),
        "indicator": lambda gui, control_type, attrs: _Builder(
            gui=gui,
            control_type=control_type,
            element_name="Indicator",
            attributes=attrs,
        )
        .set_value_and_default(with_update=False, native_type=True)
        .set_attributes(
            [
                ("id",),
                ("min", _AttributeType.number),
                ("max", _AttributeType.number),
                ("value", _AttributeType.dynamic_number),
                ("format",),
                ("orientation"),
                ("hover_text", _AttributeType.dynamic_string),
            ]
        ),
        "input": lambda gui, control_type, attrs: _Builder(
            gui=gui,
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
                ("active", _AttributeType.dynamic_boolean, True),
                ("hover_text", _AttributeType.dynamic_string),
            ]
        ),
        "layout": lambda gui, control_type, attrs: _Builder(
            gui=gui, control_type=control_type, element_name="Layout", attributes=attrs, default_value=None
        )
        .set_value_and_default(with_default=False)
        .set_attributes(
            [
                ("id",),
                ("columns[mobile]",),
                ("gap",),
            ]
        ),
        "menu": lambda gui, control_type, attrs: _Builder(
            gui=gui,
            control_type=control_type,
            element_name="MenuCtl",
            attributes=attrs,
        )
        .get_adapter("lov")  # need to be called before set_lov
        .set_lov()
        .set_attributes(
            [
                ("id",),
                ("active", _AttributeType.dynamic_boolean, True),
                ("label"),
                ("width"),
                ("width[mobile]",),
                ("on_action", _AttributeType.function, "on_menu_action"),
                ("inactive_ids", _AttributeType.dynamic_list),
                ("hover_text", _AttributeType.dynamic_string),
            ]
        )
        .set_refresh_on_update()
        .set_propagate(),
        "navbar": lambda gui, control_type, attrs: _Builder(
            gui=gui, control_type=control_type, element_name="NavBar", attributes=attrs, default_value=None
        )
        .get_adapter("lov", multi_selection=False)  # need to be called before set_lov
        .set_lov()
        .set_attributes(
            [
                ("id",),
                ("active", _AttributeType.dynamic_boolean, True),
                ("hover_text", _AttributeType.dynamic_string),
            ]
        ),
        "number": lambda gui, control_type, attrs: _Builder(
            gui=gui,
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
                ("active", _AttributeType.dynamic_boolean, True),
                ("hover_text", _AttributeType.dynamic_string),
            ]
        ),
        "pane": lambda gui, control_type, attrs: _Builder(
            gui=gui, control_type=control_type, element_name="Pane", attributes=attrs, default_value=None
        )
        .set_value_and_default(var_type=_AttributeType.dynamic_boolean)
        .set_partial()  # partial should be set before page
        .set_attributes(
            [
                ("id",),
                ("page",),
                ("anchor", _AttributeType.string, "left"),
                ("on_close", _AttributeType.function),
                ("persistent", _AttributeType.boolean, False),
                ("active", _AttributeType.dynamic_boolean, True),
                ("width", _AttributeType.string_or_number, "30vw"),
                ("height", _AttributeType.string_or_number, "30vh"),
                ("hover_text", _AttributeType.dynamic_string),
            ]
        )
        .set_propagate(),
        "part": lambda gui, control_type, attrs: _Builder(
            gui=gui, control_type=control_type, element_name="Part", attributes=attrs, default_value=None
        )
        .set_value_and_default(with_update=False, var_type=_AttributeType.dynamic_boolean, default_val=True)
        .set_partial()  # partial should be set before page
        .set_attributes(
            [
                ("id",),
                ("page",),
            ]
        ),
        "selector": lambda gui, control_type, attrs: _Builder(
            gui=gui,
            control_type=control_type,
            element_name="Selector",
            attributes=attrs,
        )
        .set_value_and_default(with_default=False, var_type=_AttributeType.lov_value)
        .get_adapter("lov")  # need to be called before set_lov
        .set_lov()
        .set_attributes(
            [
                ("filter", _AttributeType.boolean),
                ("multiple", _AttributeType.boolean),
                ("dropdown", _AttributeType.boolean, False),
                ("id",),
                ("active", _AttributeType.dynamic_boolean, True),
                ("height", _AttributeType.string_or_number),
                ("width", _AttributeType.string_or_number),
                ("hover_text", _AttributeType.dynamic_string),
            ]
        )
        .set_refresh_on_update()
        .set_propagate(),
        "slider": lambda gui, control_type, attrs: _Builder(
            gui=gui,
            control_type=control_type,
            element_name="Slider",
            attributes=attrs,
            default_value=0,
        )
        .set_value_and_default(native_type=True)
        .set_attributes(
            [
                ("min", _AttributeType.number, 0),
                ("max", _AttributeType.number, 100),
                ("id",),
                ("active", _AttributeType.dynamic_boolean, True),
                ("width", _AttributeType.string, "300px"),
                ("height"),
                ("orientation"),
                ("hover_text", _AttributeType.dynamic_string),
            ]
        )
        .get_adapter("lov")  # need to be called before set_lov
        .set_lov()
        .set_labels()
        .set_string_with_check("text_anchor", _Factory.__TEXT_ANCHORS + [_Factory.__TEXT_ANCHOR_NONE], "bottom")
        .set_propagate(),
        "status": lambda gui, control_type, attrs: _Builder(
            gui=gui,
            control_type=control_type,
            element_name="Status",
            attributes=attrs,
        )
        .set_value_and_default(with_update=False)
        .set_attributes(
            [
                ("id",),
                ("without_close", _AttributeType.boolean, False),
                ("hover_text", _AttributeType.dynamic_string),
            ]
        )
        .set_refresh_on_update(),
        "table": lambda gui, control_type, attrs: _Builder(
            gui=gui,
            control_type=control_type,
            element_name="Table",
            attributes=attrs,
        )
        .set_value_and_default(with_default=False, var_type=_AttributeType.data)
        .get_dataframe_attributes()
        .set_attributes(
            [
                ("page_size", _AttributeType.react, 100),
                ("allow_all_rows", _AttributeType.boolean),
                ("show_all", _AttributeType.boolean),
                ("auto_loading", _AttributeType.boolean),
                ("width", _AttributeType.string_or_number, "100vw"),
                ("height", _AttributeType.string_or_number, "80vh"),
                ("id",),
                ("active", _AttributeType.dynamic_boolean, True),
                ("editable", _AttributeType.dynamic_boolean, True),
                ("on_edit", _AttributeType.function),
                ("on_delete", _AttributeType.function),
                ("on_add", _AttributeType.function),
                ("nan_value",),
                ("hover_text", _AttributeType.dynamic_string),
            ]
        )
        .set_refresh()
        .set_propagate()
        .get_list_attribute("selected", _AttributeType.number)
        .set_refresh_on_update()
        .set_table_pagesize_options(),
        "text": lambda gui, control_type, attrs: _Builder(
            gui=gui,
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
                ("hover_text", _AttributeType.dynamic_string),
            ]
        ),
        "toggle": lambda gui, control_type, attrs: _Builder(
            gui=gui, control_type=control_type, element_name="Toggle", attributes=attrs, default_value=None
        )
        .set_value_and_default(with_default=False, var_type=_AttributeType.lov_value)
        .get_adapter("lov", multi_selection=False)  # need to be called before set_lov
        .set_lov()
        .set_attributes(
            [
                ("id",),
                ("label",),
                ("active", _AttributeType.dynamic_boolean, True),
                ("unselected_value", _AttributeType.string, ""),
                ("hover_text", _AttributeType.dynamic_string),
            ]
        )
        .set_kind()
        .set_refresh_on_update()
        .set_propagate(),
        "tree": lambda gui, control_type, attrs: _Builder(
            gui=gui,
            control_type=control_type,
            element_name="TreeView",
            attributes=attrs,
        )
        .set_value_and_default(with_default=False, var_type=_AttributeType.lov_value)
        .get_adapter("lov")  # need to be called before set_lov
        .set_lov()
        .set_attributes(
            [
                ("filter", _AttributeType.boolean),
                ("multiple", _AttributeType.boolean),
                ("expanded", _AttributeType.boolean_or_list, True),
                ("id",),
                ("active", _AttributeType.dynamic_boolean, True),
                ("height", _AttributeType.string_or_number),
                ("width", _AttributeType.string_or_number),
                ("hover_text", _AttributeType.dynamic_string),
            ]
        )
        .set_refresh_on_update()
        .set_propagate(),
    }

    # TODO: process \" in property value
    _PROPERTY_RE = re.compile(r"\s+([a-zA-Z][\.a-zA-Z_$0-9]*(?:\[(?:.*?)\])?)=\"((?:(?:(?<=\\)\")|[^\"])*)\"")

    @staticmethod
    def get_default_property_name(control_name: str) -> t.Optional[str]:
        return _Factory.__CONTROL_DEFAULT_PROP_NAME.get(control_name.split(".", 1)[0])
