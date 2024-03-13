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
    from ._renderers import _Element  # noqa: F401


class Page:
    """Generic page generator.

    The `Page` class transforms template text into actual pages that can be displayed
    on a web browser.

    When a page is requested to be displayed, it is converted into HTML
    code that can be sent to the client. All control placeholders are
    replaced by their respective graphical component so you can show
    your application variables and interact with them.
    """

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
            funcs = [
                i[0]
                for i in inspect.getmembers(cls)
                if not i[0].startswith("_") and (inspect.ismethod(i[1]) or inspect.isfunction(i[1]))
            ]
            for f in funcs:
                func = getattr(self, f)
                if hasattr(func, "__func__") and func.__func__ is not None:
                    cls_locals[f] = func.__func__
            self._class_module_name = cls.__name__
            self._class_locals = cls_locals

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

    def _get_locals(self) -> t.Optional[t.Dict[str, t.Any]]:
        return (
            self._class_locals
            if self._is_class_module()
            else None if (frame := self._get_frame()) is None else _filter_locals(frame.f_locals)
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
