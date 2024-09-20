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

# _Page for multipage support
from __future__ import annotations

import logging
import typing as t
import warnings

if t.TYPE_CHECKING:
    from ._renderers import Page
    from .gui import Gui


class _Page(object):
    def __init__(self) -> None:
        self._rendered_jsx: t.Optional[str] = None
        self._renderer: t.Optional[Page] = None
        self._style: t.Optional[t.Union[str, t.Dict[str, t.Any]]] = None
        self._route: t.Optional[str] = None
        self._head: t.Optional[list] = None

    def render(self, gui: Gui, silent: t.Optional[bool] = False):
        if self._renderer is None:
            raise RuntimeError(f"Can't render page {self._route}: no renderer found")
        with warnings.catch_warnings(record=True) as w:
            warnings.resetwarnings()
            with gui._set_locals_context(self._renderer._get_module_name()):
                self._rendered_jsx = self._renderer.render(gui)
            if not silent and w:
                s = "\033[1;31m\n"
                s += (
                    message
                    := f"--- {len(w)} warning(s) were found for page '{'/' if self._route == gui._get_root_page_name() else self._route}' {self._renderer._get_content_detail(gui)} ---\n"  # noqa: E501
                )
                for i, wm in enumerate(w):
                    s += f" - Warning {i + 1}: {wm.message}\n"
                s += "-" * len(message)
                s += "\033[0m\n"
                logging.warn(s)
        if hasattr(self._renderer, "head"):
            self._head = list(self._renderer.head)  # type: ignore
        # return renderer module_name from frame
        return self._renderer._get_module_name()
