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

import time
import typing as t
from dataclasses import dataclass, field
from threading import Lock
from weakref import WeakKeyDictionary

from ._page import _Page
from ._warnings import _warn
from .state import State

if t.TYPE_CHECKING:
    from .page import Page
    from .gui import Gui


@dataclass
class UpdateQueue:
    """
    A queue system to manage partial content updates.

    Arguments:
        updates (WeakKeyDictionary): stores updates per GUI instance using weak references.
        last_update (float): Timestamp of the last processed update.
        lock (Lock): Thread lock for synchronization.
    """
    updates: WeakKeyDictionary = field(default_factory=WeakKeyDictionary)
    last_update: float = field(default_factory=lambda: time.time())
    lock: Lock = field(default_factory=Lock)


class Partial(_Page):
    """Reusable Page content.

    Partials are used when you need to use a partial page content in different
    and not related pages. This allows not to have to repeat yourself when
    creating your page templates.

    Visual elements such as [`part`](../../../../../refmans/gui/viselements/generic/part.md),
    [`dialog`](../../../../../refmans/gui/viselements/generic/dialog.md) or
    [`pane`](../../../../../refmans/gui/viselements/generic/pane.md) can use Partials.

    Note that `Partial` has no constructor (no `__init__()` method): to create a
    `Partial`, you must call the `Gui.add_partial()^` function.

    Partials can be really handy if you want to modify a section of a page:
    the `update_content()` method dynamically update pages that make use
    of this `Partial` therefore making it easy to change the content of
    any page, at any moment.
    """

    _PARTIALS = "__partials"

    __partials: t.Dict[str, Partial] = {}

    __update_queues: t.Dict[str, UpdateQueue] = {}

    STREAM_MODE_BATCH_INTERVAL = 0.05
    STANDARD_BATCH_INTERVAL = 0.2

    def __init__(self, route: t.Optional[str] = None):
        super().__init__()
        if route is None:
            self._route: str = f"TaiPy_partials_{len(Partial.__partials)}"
            Partial.__partials[self._route] = self
        else:
            self._route = route

        if self._route not in Partial.__update_queues:
            Partial.__update_queues[self._route] = UpdateQueue()

    def update_content(self, state: State, content: t.Union[str, "Page"], stream_mode: bool = False):
        """Update partial content.

        Arguments:
            state (State^): The current user state as received in any callback.
            content (str): The new content to use and display.
            stream_mode (bool): If True, uses shorter batch interval for smoother streaming.
        """
        if state and state._gui and callable(state._gui._update_partial):
            state._gui._update_partial(self.__copy(content))
        else:
            _warn("'Partial.update_content()' must be called in the context of a callback.")

        gui_id = get_state_id(state)
        queue = Partial.__update_queues[self._route]
        current_time = time.time()
        batch_interval = self.STREAM_MODE_BATCH_INTERVAL if stream_mode else self.STANDARD_BATCH_INTERVAL

        with queue.lock:
            queue.updates.setdefault(state._gui, []).append((current_time, self.__copy(content)))
            if current_time - queue.last_update >= batch_interval:
                self._process_updates(state)
                queue.last_update = current_time

    def _process_updates(self, state: State, gui_id: str):
        queue = Partial.__update_queues[self._route]
        with queue.lock:
            gui_updates = t.list[t.Tuple[float, Partial]] = queue.updates.get(gui_id, [])
            if not gui_updates:
                return

            _, latest_content = gui_updates[-1]
            gui_updates.clear()
            state._gui._update_partial(latest_content)

    def __copy(self, content: t.Union[str, "Page"]) -> Partial:
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

    @classmethod
    def force_update(cls, state: State, route: str):
        if route in cls.__update_queues:
            queue = cls.__update_queues[route]
            with queue.lock:
                cls.__partials[route]._process_updates(state)
