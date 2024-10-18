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

from ...gui import Gui, State


class TestingState(State):
    __VARS = "vars"

    def __init__(self, gui: Gui, **kwargs) -> None:
        super().__setattr__(TestingState.__VARS, kwargs)
        super().__init__(gui, [], [])

    def __getattribute__(self, name: str) -> t.Any:
        if attr := t.cast(dict, super().__getattribute__(TestingState.__VARS)).get(name):
            return attr
        try:
            return super().__getattribute__(name)
        except Exception:
            return None

    def __setattr__(self, name: str, value: t.Any) -> None:
        t.cast(dict, super().__getattribute__(TestingState.__VARS))[name] = value

    def __getitem__(self, key: str):
        return self
