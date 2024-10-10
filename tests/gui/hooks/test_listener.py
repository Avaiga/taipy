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
import time
import typing as t
from unittest.mock import MagicMock

from taipy.gui import Gui
from taipy.gui._hook import _Hook, _Hooks


def test_empty_listener(gui: Gui):
    listener = MagicMock()
    event = "an_event"
    payload = {"a": 1}

    gui._add_event_listener(event, listener)

    gui._fire_event(event, None, payload)

    listener.assert_not_called()

def test_listener(gui: Gui):
    class ListenerHook(_Hook):
        method_names = ["_add_event_listener", "_fire_event"]

        def __init__(self):
            super().__init__()
            self.listeners = {}

        def _add_event_listener(
            self,
            event_name: str,
            listener: t.Callable[[str, t.Dict[str, t.Any]], None],
            with_state: t.Optional[bool] = False,
        ):
            self.listeners[event_name] = listener

        def _fire_event(
            self, event_name: str, client_id: t.Optional[str] = None, payload: t.Optional[t.Dict[str, t.Any]] = None
        ):
            if func := self.listeners.get(event_name):
                func(event_name, client_id, payload)

    gui.run(run_server=False, single_client=True, stylekit=False)

    _Hooks()._register_hook(ListenerHook())

    listener = MagicMock()
    event = "an_event"
    payload = {"a": 1}

    gui._add_event_listener(event, listener)

    with gui._Gui__event_manager: # type: ignore[attr-defined]
        gui._fire_event(event, None, payload)

    time.sleep(0.3)
    listener.assert_called_once_with(event, None, payload)
