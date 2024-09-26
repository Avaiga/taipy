# Copyright 2021-2024 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import re
import typing as t
from datetime import datetime

from ..types import PropertyType
from .builder import _Builder

if t.TYPE_CHECKING:
    from ..extension.library import ElementLibrary
    from ..gui import Gui


class _Factory:
    DEFAULT_CONTROL = "text"

    _START_SUFFIX = ".start"
    _END_SUFFIX = ".end"

    __TAIPY_NAME_SPACE = "taipy."

    __CONTROL_DEFAULT_PROP_NAME = {
        "button": "label",
        "chat": "messages",
        "chart": "data",
        "content": "value",
        "date": "date",
        "date_range": "dates",
        "dialog": "open",
        "expandable": "title",
        "file_download": "content",
        "file_selector": "content",
        "image": "content",
        "indicator": "display",
        "input": "value",
        "layout": "columns",
        "login": "title",
        "menu": "lov",
        "metric": "value",
        "navbar": "value",
        "number": "value",
        "pane": "open",
        "part": "class_name",
        "progress": "value",
        "selector": "value",
        "slider": "value",
        "status": "value",
        "table": "data",
        "text": "value",
        "toggle": "value",
        "tree": "value",
    }

    _TEXT_ATTRIBUTES = ["format", "id", "hover_text", "raw"]

    __TEXT_ANCHORS = ["bottom", "top", "left", "right"]
    __TEXT_ANCHOR_NONE = "none"

    __LIBRARIES: t.Dict[str, t.List["ElementLibrary"]] = {}

    __CONTROL_BUILDERS = {
        "button": lambda gui, control_type, attrs: _Builder(
            gui=gui,
            control_type=control_type,
            element_name="Button",
            attributes=attrs,
        )
        .set_value_and_default(with_update=False)
        .set_attributes(
            [
                ("on_action", PropertyType.function),
                ("active", PropertyType.dynamic_boolean, True),
                ("hover_text", PropertyType.dynamic_string),
                ("width", PropertyType.string_or_number),
            ]
        ),
        "chat": lambda gui, control_type, attrs: _Builder(
            gui=gui, control_type=control_type, element_name="Chat", attributes=attrs, default_value=None
        )
        .set_value_and_default(with_update=True, with_default=False, var_type=PropertyType.data)
        .set_attributes(
            [
                ("on_action", PropertyType.function),
                ("active", PropertyType.dynamic_boolean, True),
                ("hover_text", PropertyType.dynamic_string),
                ("with_input", PropertyType.dynamic_boolean, True),
                ("users", PropertyType.lov),
                ("sender_id",),
                ("height",),
                ("page_size", PropertyType.number, 50),
                ("show_sender", PropertyType.boolean, False),
                ("mode",),
            ]
        ),
        "chart": lambda gui, control_type, attrs: _Builder(
            gui=gui, control_type=control_type, element_name="Chart", attributes=attrs, default_value=None
        )
        .set_value_and_default(with_default=False, var_type=PropertyType.data)
        .set_attributes(
            [
                ("title",),
                ("width", PropertyType.string_or_number),
                ("height", PropertyType.string_or_number),
                ("layout", PropertyType.dynamic_dict),
                ("plot_config", PropertyType.dict),
                ("on_range_change", PropertyType.function),
                ("active", PropertyType.dynamic_boolean, True),
                ("render", PropertyType.dynamic_boolean, True),
                ("hover_text", PropertyType.dynamic_string),
                ("on_change", PropertyType.function),
                ("template", PropertyType.dict),
                ("template[dark]", PropertyType.dict, gui._get_config("chart_dark_template", None)),
                ("template[light]", PropertyType.dict),
                ("figure", PropertyType.to_json),
                ("on_click", PropertyType.function),
            ]
        )
        ._get_chart_config("scatter", "lines+markers")
        ._set_propagate(),
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
        .set_value_and_default(var_type=PropertyType.date)
        .set_attributes(
            [
                ("with_time", PropertyType.boolean),
                ("active", PropertyType.dynamic_boolean, True),
                ("min", PropertyType.dynamic_date),
                ("max", PropertyType.dynamic_date),
                ("editable", PropertyType.dynamic_boolean, True),
                ("hover_text", PropertyType.dynamic_string),
                ("label",),
                ("on_change", PropertyType.function),
                ("format",),
                ("width", PropertyType.string_or_number),
            ]
        )
        ._set_propagate(),
        "date_range": lambda gui, control_type, attrs: _Builder(
            gui=gui,
            control_type=control_type,
            element_name="DateRange",
            attributes=attrs,
        )
        .set_value_and_default(var_type=PropertyType.date_range)
        .set_attributes(
            [
                ("with_time", PropertyType.boolean),
                ("active", PropertyType.dynamic_boolean, True),
                ("editable", PropertyType.dynamic_boolean, True),
                ("hover_text", PropertyType.dynamic_string),
                ("label_start",),
                ("label_end",),
                ("on_change", PropertyType.function),
                ("format",),
                ("width", PropertyType.string_or_number),
            ]
        )
        ._set_propagate(),
        "dialog": lambda gui, control_type, attrs: _Builder(
            gui=gui,
            control_type=control_type,
            element_name="Dialog",
            attributes=attrs,
        )
        .set_value_and_default(var_type=PropertyType.dynamic_boolean)
        ._set_partial()  # partial should be set before page
        .set_attributes(
            [
                ("page",),
                ("title",),
                ("on_action", PropertyType.function),
                ("close_label", PropertyType.string),
                ("labels", PropertyType.string_list),
                ("active", PropertyType.dynamic_boolean, True),
                ("width", PropertyType.string_or_number),
                ("height", PropertyType.string_or_number),
                ("hover_text", PropertyType.dynamic_string),
            ]
        )
        ._set_propagate(),
        "expandable": lambda gui, control_type, attrs: _Builder(
            gui=gui, control_type=control_type, element_name="Expandable", attributes=attrs, default_value=None
        )
        .set_value_and_default()
        ._set_partial()  # partial should be set before page
        .set_attributes(
            [
                ("page",),
                ("expanded", PropertyType.dynamic_boolean, True, True, False),
                ("hover_text", PropertyType.dynamic_string),
                ("on_change", PropertyType.function),
            ]
        ),
        "file_download": lambda gui, control_type, attrs: _Builder(
            gui=gui,
            control_type=control_type,
            element_name="FileDownload",
            attributes=attrs,
        )
        .set_value_and_default(var_name="label", with_update=False)
        ._set_content("content", image=False)
        .set_attributes(
            [
                ("on_action", PropertyType.function),
                ("active", PropertyType.dynamic_boolean, True),
                ("render", PropertyType.dynamic_boolean, True),
                ("auto", PropertyType.boolean, False),
                ("bypass_preview", PropertyType.boolean, True),
                ("name",),
                ("hover_text", PropertyType.dynamic_string),
                ("width", PropertyType.string_or_number),
            ]
        ),
        "file_selector": lambda gui, control_type, attrs: _Builder(
            gui=gui,
            control_type=control_type,
            element_name="FileSelector",
            attributes=attrs,
        )
        .set_value_and_default(var_name="label", with_update=False)
        ._set_file_content()
        .set_attributes(
            [
                ("on_action", PropertyType.function),
                ("active", PropertyType.dynamic_boolean, True),
                ("multiple", PropertyType.boolean, False),
                ("extensions",),
                ("drop_message",),
                ("hover_text", PropertyType.dynamic_string),
                ("notify", PropertyType.boolean, True),
                ("width", PropertyType.string_or_number),
            ]
        ),
        "image": lambda gui, control_type, attrs: _Builder(
            gui=gui,
            control_type=control_type,
            element_name="Image",
            attributes=attrs,
        )
        .set_value_and_default(var_name="label", with_update=False)
        ._set_content("content")
        .set_attributes(
            [
                ("on_action", PropertyType.function),
                ("active", PropertyType.dynamic_boolean, True),
                ("width",),
                ("height",),
                ("hover_text", PropertyType.dynamic_string),
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
                ("min", PropertyType.number),
                ("max", PropertyType.number),
                ("value", PropertyType.dynamic_number),
                ("format",),
                ("orientation",),
                ("width",),
                ("height",),
            ]
        ),
        "input": lambda gui, control_type, attrs: _Builder(
            gui=gui,
            control_type=control_type,
            element_name="Input",
            attributes=attrs,
        )
        ._set_input_type("text", True)
        .set_value_and_default()
        ._set_propagate()
        .set_attributes(
            [
                ("active", PropertyType.dynamic_boolean, True),
                ("hover_text", PropertyType.dynamic_string),
                ("on_change", PropertyType.function),
                ("on_action", PropertyType.function),
                ("action_keys",),
                ("label",),
                ("change_delay", PropertyType.number, gui._get_config("change_delay", None)),
                ("multiline", PropertyType.boolean, False),
                ("lines_shown", PropertyType.number, 5),
                ("width", PropertyType.string_or_number),
            ]
        ),
        "layout": lambda gui, control_type, attrs: _Builder(
            gui=gui, control_type=control_type, element_name="Layout", attributes=attrs, default_value=None
        )
        .set_value_and_default(with_default=False)
        .set_attributes(
            [
                ("columns[mobile]",),
                ("gap",),
            ]
        ),
        "login": lambda gui, control_type, attrs: _Builder(
            gui=gui, control_type=control_type, element_name="Login", attributes=attrs, default_value=None
        )
        .set_value_and_default(default_val="Log-in")
        .set_attributes(
            [
                ("message", PropertyType.dynamic_string),
                ("on_action", PropertyType.function, "on_login"),
            ]
        ),
        "menu": lambda gui, control_type, attrs: _Builder(
            gui=gui,
            control_type=control_type,
            element_name="MenuCtl",
            attributes=attrs,
        )
        .set_attributes(
            [
                ("active", PropertyType.dynamic_boolean, True),
                ("label",),
                ("width",),
                ("width[mobile]",),
                ("on_action", PropertyType.function),
                ("inactive_ids", PropertyType.dynamic_list),
                ("hover_text", PropertyType.dynamic_string),
                ("lov", PropertyType.lov),
            ]
        )
        ._set_propagate(),
        "metric": lambda gui, control_type, attrs: _Builder(
            gui=gui,
            control_type=control_type,
            element_name="Metric",
            attributes=attrs,
        )
        .set_value_and_default(var_type=PropertyType.dynamic_number, native_type=True)
        .set_attributes(
            [
                ("title",),
                ("active", PropertyType.dynamic_boolean, True),
                ("layout", PropertyType.dynamic_dict),
                ("type", PropertyType.string, "circular"),
                ("min", PropertyType.number, 0),
                ("max", PropertyType.number, 100),
                ("delta", PropertyType.dynamic_number),
                ("delta_color", PropertyType.string),
                ("negative_delta_color", PropertyType.string),
                ("threshold", PropertyType.dynamic_number),
                ("width", PropertyType.string_or_number),
                ("height", PropertyType.string_or_number),
                ("show_value", PropertyType.boolean, True),
                ("format", PropertyType.string),
                ("delta_format", PropertyType.string),
                ("bar_color", PropertyType.string),
                ("color_map", PropertyType.dict),
                ("hover_text", PropertyType.dynamic_string),
                ("template", PropertyType.dict),
                ("template[dark]", PropertyType.dict),
                ("template[light]", PropertyType.dict),
            ]
        ),
        "navbar": lambda gui, control_type, attrs: _Builder(
            gui=gui, control_type=control_type, element_name="NavBar", attributes=attrs, default_value=None
        ).set_attributes(
            [
                ("active", PropertyType.dynamic_boolean, True),
                ("hover_text", PropertyType.dynamic_string),
                ("lov", PropertyType.single_lov),
            ]
        ),
        "number": lambda gui, control_type, attrs: _Builder(
            gui=gui,
            control_type=control_type,
            element_name="Input",
            attributes=attrs,
            default_value=0,
        )
        ._set_input_type("number")
        .set_value_and_default(var_type=PropertyType.dynamic_number)
        ._set_propagate()
        .set_attributes(
            [
                ("active", PropertyType.dynamic_boolean, True),
                ("step", PropertyType.dynamic_number, 1),
                ("step_multiplier", PropertyType.dynamic_number, 10),
                ("min", PropertyType.dynamic_number),
                ("max", PropertyType.dynamic_number),
                ("hover_text", PropertyType.dynamic_string),
                ("on_change", PropertyType.function),
                ("on_action", PropertyType.function),
                ("label",),
                ("change_delay", PropertyType.number, gui._get_config("change_delay", None)),
                ("width", PropertyType.string_or_number),
            ]
        ),
        "pane": lambda gui, control_type, attrs: _Builder(
            gui=gui, control_type=control_type, element_name="Pane", attributes=attrs, default_value=None
        )
        .set_value_and_default(var_type=PropertyType.dynamic_boolean)
        ._set_partial()  # partial should be set before page
        .set_attributes(
            [
                ("page",),
                ("anchor", PropertyType.string, "left"),
                ("on_close", PropertyType.function),
                ("persistent", PropertyType.boolean, False),
                ("active", PropertyType.dynamic_boolean, True),
                ("width", PropertyType.string_or_number, "30vw"),
                ("height", PropertyType.string_or_number, "30vh"),
                ("hover_text", PropertyType.dynamic_string),
                ("on_change", PropertyType.function),
                ("show_button", PropertyType.boolean, False),
            ]
        )
        ._set_propagate(),
        "part": lambda gui, control_type, attrs: _Builder(
            gui=gui, control_type=control_type, element_name="Part", attributes=attrs, default_value=None
        )
        ._set_partial()  # partial should be set before page
        .set_attributes(
            [
                ("page", PropertyType.dynamic_string),
                ("render", PropertyType.dynamic_boolean, True),
                ("height", PropertyType.dynamic_string),
                ("content", PropertyType.toHtmlContent),
                ("width", PropertyType.string_or_number),
            ]
        ),
        "progress": lambda gui, control_type, attrs: _Builder(
            gui=gui,
            control_type=control_type,
            element_name="Progress",
            attributes=attrs,
        )
        .set_value_and_default(var_type=PropertyType.dynamic_number, native_type=True)
        .set_attributes(
            [
                ("linear", PropertyType.boolean, False),
                ("show_value", PropertyType.boolean, False),
                ("title", PropertyType.dynamic_string),
                ("title_anchor", PropertyType.string, "bottom"),
                ("render", PropertyType.dynamic_boolean, True),
                ("width", PropertyType.string_or_number),
            ]
        ),
        "selector": lambda gui, control_type, attrs: _Builder(
            gui=gui, control_type=control_type, element_name="Selector", attributes=attrs, default_value=None
        )
        .set_value_and_default(with_default=False, var_type=PropertyType.lov_value)
        .set_attributes(
            [
                ("active", PropertyType.dynamic_boolean, True),
                ("dropdown", PropertyType.boolean, False),
                ("filter", PropertyType.boolean),
                ("height", PropertyType.string_or_number),
                ("hover_text", PropertyType.dynamic_string),
                ("value_by_id", PropertyType.boolean),
                ("multiple", PropertyType.boolean),
                ("width", PropertyType.string_or_number),
                ("on_change", PropertyType.function),
                ("label",),
                ("mode",),
                ("lov", PropertyType.lov),
            ]
        )
        ._set_propagate(),
        "slider": lambda gui, control_type, attrs: _Builder(
            gui=gui,
            control_type=control_type,
            element_name="Slider",
            attributes=attrs,
            default_value=0,
        )
        .set_value_and_default(native_type=True, var_type=PropertyType.slider_value)
        .set_attributes(
            [
                ("active", PropertyType.dynamic_boolean, True),
                ("height",),
                ("hover_text", PropertyType.dynamic_string),
                ("value_by_id", PropertyType.boolean),
                ("max", PropertyType.number, 100),
                ("min", PropertyType.number, 0),
                ("step", PropertyType.number, 1),
                ("orientation",),
                ("width", PropertyType.string, "300px"),
                ("on_change", PropertyType.function),
                ("continuous", PropertyType.boolean, None),
                ("lov", PropertyType.lov),
                ("change_delay", PropertyType.number, gui._get_config("change_delay", None)),
            ]
        )
        ._set_labels()
        ._set_string_with_check("text_anchor", _Factory.__TEXT_ANCHORS + [_Factory.__TEXT_ANCHOR_NONE], "bottom")
        ._set_propagate(),
        "status": lambda gui, control_type, attrs: _Builder(
            gui=gui,
            control_type=control_type,
            element_name="Status",
            attributes=attrs,
        )
        .set_value_and_default(with_update=False)
        .set_attributes(
            [
                ("without_close", PropertyType.boolean, False),
                ("hover_text", PropertyType.dynamic_string),
            ]
        ),
        "table": lambda gui, control_type, attrs: _Builder(
            gui=gui,
            control_type=control_type,
            element_name="Table",
            attributes=attrs,
        )
        .set_value_and_default(with_default=False, var_type=PropertyType.data)
        ._get_dataframe_attributes()
        ._get_list_attribute("selected", PropertyType.number)
        .set_attributes(
            [
                ("page_size", PropertyType.number, "100"),
                ("allow_all_rows", PropertyType.boolean),
                ("show_all", PropertyType.boolean),
                ("auto_loading", PropertyType.boolean),
                ("width", PropertyType.string_or_number, "100%"),
                ("height", PropertyType.string_or_number, "80vh"),
                ("active", PropertyType.dynamic_boolean, True),
                ("editable", PropertyType.dynamic_boolean, False),
                ("on_edit", PropertyType.function, gui._get_call_method_name("table_on_edit")),
                ("on_delete", PropertyType.function, gui._get_call_method_name("table_on_delete")),
                ("on_add", PropertyType.function, gui._get_call_method_name("table_on_add")),
                ("on_action", PropertyType.function),
                ("nan_value",),
                ("filter", PropertyType.boolean),
                ("hover_text", PropertyType.dynamic_string),
                ("size",),
                ("downloadable", PropertyType.boolean),
                ("use_checkbox", PropertyType.boolean),
            ]
        )
        ._set_propagate()
        ._set_table_pagesize_options(),
        "text": lambda gui, control_type, attrs: _Builder(
            gui=gui,
            control_type=control_type,
            element_name="Field",
            attributes=attrs,
        )
        .set_value_and_default(with_update=False)
        ._set_dataType()
        .set_attributes(
            [
                ("format",),
                ("hover_text", PropertyType.dynamic_string),
                ("raw", PropertyType.boolean, False),
                ("mode",),
                ("width", PropertyType.string_or_number),
            ]
        ),
        "toggle": lambda gui, control_type, attrs: _Builder(
            gui=gui, control_type=control_type, element_name="Toggle", attributes=attrs, default_value=None
        )
        .set_value_and_default(with_default=False, var_type=PropertyType.toggle_value)
        .set_attributes(
            [
                ("active", PropertyType.dynamic_boolean, True),
                ("hover_text", PropertyType.dynamic_string),
                ("label",),
                ("value_by_id", PropertyType.boolean),
                ("unselected_value", PropertyType.string, ""),
                ("allow_unselect", PropertyType.boolean),
                ("on_change", PropertyType.function),
                ("mode",),
                ("lov", PropertyType.single_lov),
                ("width", PropertyType.string_or_number),
            ]
        )
        ._set_kind()
        ._set_propagate(),
        "tree": lambda gui, control_type, attrs: _Builder(
            gui=gui,
            control_type=control_type,
            element_name="TreeView",
            attributes=attrs,
        )
        .set_value_and_default(with_default=False, var_type=PropertyType.lov_value)
        .set_attributes(
            [
                ("active", PropertyType.dynamic_boolean, True),
                ("expanded", PropertyType.boolean_or_list, True),
                ("filter", PropertyType.boolean),
                ("hover_text", PropertyType.dynamic_string),
                ("height", PropertyType.string_or_number),
                ("value_by_id", PropertyType.boolean),
                ("multiple", PropertyType.boolean),
                ("width", PropertyType.string_or_number),
                ("on_change", PropertyType.function),
                ("select_leafs_only", PropertyType.boolean),
                ("row_height", PropertyType.string),
                ("lov", PropertyType.lov),
            ]
        )
        ._set_propagate(),
    }

    # TODO: process \" in property value
    _PROPERTY_RE = re.compile(r"\s+([a-zA-Z][\.a-zA-Z_$0-9]*(?:\[(?:.*?)\])?)=\"((?:(?:(?<=\\)\")|[^\"])*)\"")

    __COUNTER = 0

    @staticmethod
    def set_library(library: "ElementLibrary"):
        from ..extension.library import Element, ElementLibrary

        if isinstance(library, ElementLibrary) and isinstance(library.get_name(), str) and library.get_elements():
            elements = library.get_elements()
            for name, element in elements.items():
                if isinstance(element, Element):
                    element.check(name)
            fact_lib = _Factory.__LIBRARIES.get(library.get_name())
            if fact_lib is None:
                _Factory.__LIBRARIES.update({library.get_name(): [library]})
            else:
                fact_lib.append(library)

    @staticmethod
    def get_default_property_name(control_name: str) -> t.Optional[str]:
        name = (
            control_name[: -len(_Factory._START_SUFFIX)]
            if control_name.endswith(_Factory._START_SUFFIX)
            else control_name[: -len(_Factory._END_SUFFIX)]
            if control_name.endswith(_Factory._END_SUFFIX)
            else control_name
        )
        name = name[len(_Factory.__TAIPY_NAME_SPACE) :] if name.startswith(_Factory.__TAIPY_NAME_SPACE) else name
        prop = _Factory.__CONTROL_DEFAULT_PROP_NAME.get(name)
        if prop is None:
            _, _, element = _Factory.__get_library_element(name)
            if element:
                prop = element.default_attribute
        return prop

    @staticmethod
    def __get_library_element(name: str):
        parts = name.split(".")
        if len(parts) > 1:
            element_name = ".".join(parts[1:])
            for lib in _Factory.__LIBRARIES.get(parts[0], []):
                elts = lib.get_elements()
                if isinstance(elts, dict):
                    if element := elts.get(element_name):
                        return lib, element_name, element
        else:
            element_name = name
            for libs in list(_Factory.__LIBRARIES.values()):
                for lib in libs:
                    elts = lib.get_elements()
                    if isinstance(elts, dict):
                        if element := elts.get(element_name):
                            return lib, element_name, element
        return None, None, None

    @staticmethod
    def call_builder(
        gui: "Gui", name: str, all_properties: t.Optional[t.Dict[str, t.Any]] = None, is_html: t.Optional[bool] = False
    ) -> t.Optional[t.Union[t.Any, t.Tuple[str, str]]]:
        name = name[len(_Factory.__TAIPY_NAME_SPACE) :] if name.startswith(_Factory.__TAIPY_NAME_SPACE) else name
        builder = _Factory.__CONTROL_BUILDERS.get(name)
        built = None
        _Factory.__COUNTER += 1
        with gui._get_authorization():
            if builder is None:
                lib, element_name, element = _Factory.__get_library_element(name)
                if lib:
                    from ..extension.library import Element

                    if isinstance(element, Element):
                        return element._call_builder(
                            element_name, gui, all_properties, lib, is_html, counter=_Factory.__COUNTER
                        )
            else:
                built = builder(gui, name, all_properties)
            if isinstance(built, _Builder):
                return built._build_to_string() if is_html else built.el
        return None
