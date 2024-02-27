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

import typing as t

from ._page import _Page
from ._warnings import _warn
from .state import State

if t.TYPE_CHECKING:
    from .page import Page


class Partial(_Page):
    """Reusable Page content.

    Partials are used when you need to use a partial page content in different
    and not related pages. This allows not to have to repeat yourself when
    creating your page templates.

    Visual elements such as [`part`](../gui/viselements/part.md),
    [`dialog`](../gui/viselements/dialog.md) or
    [`pane`](../gui/viselements/pane.md) can use Partials.

    Note that `Partial` has no constructor (no `__init__()` method): to create a
    `Partial`, you must call the `Gui.add_partial()^` function.

    Partials can be really handy if you want to modify a section of a page:
    the `update_content()` method dynamically update pages that make use
    of this `Partial` therefore making it easy to change the content of
    any page, at any moment.
    """

    _PARTIALS = "__partials"

    __partials: t.Dict[str, Partial] = {}

    def __init__(self, route: t.Optional[str] = None):
        super().__init__()
        if route is None:
            self._route = f"TaiPy_partials_{len(Partial.__partials)}"
            Partial.__partials[self._route] = self
        else:
            self._route = route

    def update_content(self, state: State, content: str | "Page"):
        """Update partial content.

        Arguments:
            state (State^): The current user state as received in any callback.
            content (str): The new content to use and display.
        """
        if state and state._gui and callable(state._gui._update_partial):
            state._gui._update_partial(self.__copy(content))
        else:
            _warn("'Partial.update_content()' must be called in the context of a callback.")

    def __copy(self, content: str | "Page") -> Partial:
        new_partial = Partial(self._route)
        from .page import Page

        if isinstance(content, Page):
            new_partial._renderer = content
        else:
            new_partial._renderer = (
                type(self._renderer)(content=content, frame=self._renderer._get_frame())
                if self._renderer is not None
                else None
            )
        return new_partial
