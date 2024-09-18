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

from .singleton import _Singleton

if t.TYPE_CHECKING:
    from ..gui import Gui


class _RuntimeManager(object, metaclass=_Singleton):
    def __init__(self) -> None:
        self.__port_gui: t.Dict[int, "Gui"] = {}

    def add_gui(self, gui: "Gui", port: int):
        if gui_port := self.__port_gui.get(port):
            gui_port.stop()
        self.__port_gui[port] = gui

    def get_used_port(self):
        return list(self.__port_gui.keys())
