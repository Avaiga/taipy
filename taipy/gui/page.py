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

from __future__ import annotations

import inspect
import typing as t
from types import FrameType

from .utils import _filter_locals, _get_module_name_from_frame

if t.TYPE_CHECKING:
    from ._page import _Page
    from .gui import Gui


class Page:
    """Generic page generator.

    The `Page` class transforms template text into actual pages that can be displayed
    on a web browser.

    When a page is requested to be displayed, it is converted into HTML
    code that can be sent to the client. All control placeholders are
    replaced by their respective graphical component so you can show
    your application variables and interact with them.
    """

    page_type: str = "Taipy"

    def __init__(self, **kwargs) -> None:
        from .custom import Page as CustomPage

        self._class_module_name = ""
        self._class_locals: t.Dict[str, t.Any] = {}
        self._frame: t.Optional[FrameType] = None
        self._renderer: t.Optional[Page] = self.create_page()
        if "frame" in kwargs:
            self._frame = kwargs.get("frame")
        elif self._renderer:
            self._frame = self._renderer._frame
        elif isinstance(self, CustomPage):
            self._frame = t.cast(FrameType, t.cast(FrameType, inspect.stack()[2].frame))
            # Allow CustomPage class to be inherited
            if len(inspect.stack()) > 3 and inspect.stack()[2].function != "<module>":
                self._frame = t.cast(FrameType, t.cast(FrameType, inspect.stack()[3].frame))
        elif len(inspect.stack()) < 4:
            raise RuntimeError(f"Can't resolve module. Page '{type(self).__name__}' is not registered.")
        else:
            self._frame = t.cast(FrameType, t.cast(FrameType, inspect.stack()[3].frame))
        if self._renderer:
            # Extract the page module's attributes and methods
            cls = type(self)
            cls_locals = dict(vars(self))
            functions = [
                i[0]
                for i in inspect.getmembers(cls)
                if not i[0].startswith("_") and inspect.isroutine(i[1])
            ]
            for f in functions:
                func = getattr(self, f)
                if hasattr(func, "__func__") and func.__func__ is not None:
                    cls_locals[f] = func.__func__
            self._class_module_name = cls.__name__
            self._class_locals = cls_locals
        # Special variables only use for page reloading in notebook context
        self._notebook_gui: t.Optional["Gui"] = None
        self._notebook_page: t.Optional["_Page"] = None
        self.set_style(kwargs.get("style", None))

    def create_page(self) -> t.Optional[Page]:
        """Create the page content for page modules.

        If this page is a page module, this method must be overloaded and return the page content.

        This method should never be called directly: only the Taipy GUI internals will.

        The default implementation returns None, indicating that this class does not implement
        a page module.

        Returns:
            The page content for this Page subclass, making it a page module.
        """
        return None

    def set_content(self, content: str) -> None:
        """Set a new page content.

        Reads the new page content and re-initializes the `Page^` instance to reflect the change.

        !!! important
            This function can only be used in an IPython notebook context.

        Arguments:
            content (str): The text content or the path to the file holding the text to be transformed.
                If *content* is a path to a readable file, the file is read entirely as the text
                template.

        Exceptions:
            RuntimeError: If this method is called outside an IPython notebook context.
        """
        # Implemented in the private _Renderer class
        raise NotImplementedError("Not in a valid Page class.")

    def _get_locals(self) -> t.Optional[t.Dict[str, t.Any]]:
        return (
            self._class_locals
            if self._is_class_module()
            else None
            if (frame := self._get_frame()) is None
            else _filter_locals(frame.f_locals)
        )

    def _is_class_module(self):
        return self._class_module_name != ""

    def _get_frame(self):
        if not hasattr(self, "_frame"):
            raise RuntimeError(f"Page '{type(self).__name__}' was not registered correctly.")
        return self._frame

    def _get_module_name(self) -> t.Optional[str]:
        return (
            None
            if (frame := self._get_frame()) is None
            else f"{_get_module_name_from_frame(frame)}{'.' if self._class_module_name else ''}{self._class_module_name}"  # noqa: E501
        )

    def _get_content_detail(self, gui) -> str:
        return f"in class {type(self).__name__}"

    def render(self, gui) -> str:
        if self._renderer is not None:
            return self._renderer.render(gui)
        return "<h1>No renderer found for page</h1>"

    def set_style(self, style: t.Dict[str, t.Dict[str, t.Any]]) -> Page:
        """Set the style for this page.

        The *style* parameter must contain a series of CSS rules that apply to the generated
        page.<br/>
        Each key of this dictionary should be a CSS selector and its associated value must be
        a CSS declaration or a CSS rule itself, benefiting from
        [nested CSS](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_nesting/Using_CSS_nesting)
        features.

        For example, you could set the *style* parameter to:
        ```python
        {
          "class1": {
            "css_property1": "css_value1",
          }
          "class2": {
            "class3": {
                "css_property2": "css_value2",
            }
          }
        }
        ```
        That would set the "css_property1" to "css_value1" for all elements with the "class1"
        class, and "css_property2" to "css_value2" for all elements with the "class3" class that
        are descendants of elements with the "class2" class.

        Arguments:
            style (dict): A dictionary describing the style as CSS or Nested CSS.

        Returns:
            This `Page` instance.
        """
        self.__style = style if isinstance(style, dict) else None
        return self

    def _get_style(self):
        return self.__style
