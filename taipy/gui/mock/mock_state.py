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
import typing as t

from .. import Gui, State
from ..utils import _MapDict


class MockState(State):
    """A Mock implementation for `State`.
    TODO
    example of use:
    ```py
    def test_callback():
        ms = MockState(Gui(""), a = 1)
        on_action(ms) # function to test
        assert ms.a == 2
    ```
    """

    __VARS = "vars"

    def __init__(self, gui: Gui, **kwargs) -> None:
        super().__setattr__(MockState.__VARS, {k: _MapDict(v) if isinstance(v, dict) else v for k, v in kwargs.items()})
        self._gui = gui
        super().__init__()

    def get_gui(self) -> Gui:
        return self._gui

    def __getattribute__(self, name: str) -> t.Any:
        if (attr := t.cast(dict, super().__getattribute__(MockState.__VARS)).get(name, None)) is not None:
            return attr
        try:
            return super().__getattribute__(name)
        except Exception:
            return None

    def __setattr__(self, name: str, value: t.Any) -> None:
        t.cast(dict, super().__getattribute__(MockState.__VARS))[name] = (
            _MapDict(value) if isinstance(value, dict) else value
        )

    def __getitem__(self, key: str):
        return self

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return True

    def broadcast(self, name: str, value: t.Any):
        pass
