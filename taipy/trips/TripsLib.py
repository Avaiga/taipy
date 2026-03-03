# Copyright 2021-2025 Avaiga Private Limited
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
from datetime import datetime

from taipy.gui.extension import Element, ElementLibrary, ElementProperty, PropertyType

from ..version import _get_version


class _Trips(ElementLibrary):
    __LIB_NAME = "trips_lib"

    __elements: dict[str, Element] = {
        "trips": Element(
            "id",
            {
                "id": ElementProperty(PropertyType.string),
                "trips": ElementProperty(PropertyType.json),
                "visible_trips": ElementProperty(PropertyType.dynamic_list),
            },
        ),
        "popup": Element(
            "title",
            {
                "id": ElementProperty(PropertyType.string),
                "title": ElementProperty(PropertyType.dynamic_string),
                "content": ElementProperty(PropertyType.dynamic_string),
                "visible": ElementProperty(PropertyType.dynamic_boolean, False),
            },
        ),
    }

    def get_name(self) -> str:
        return _Trips.__LIB_NAME

    def get_elements(self) -> t.Dict[str, Element]:
        return _Trips.__elements

    def get_scripts(self) -> t.List[str]:
        return ["lib/*.js"]

    # def on_init(self, gui: Gui) -> t.Optional[t.Tuple[str, t.Any]]:
    #     return _Trips.__CTX_VAR_NAME, self.ctx

    # def on_user_init(self, state: State):
    #     self.ctx.on_user_init(state)

    def get_version(self) -> str:
        if not hasattr(self, "version"):
            self.version = _get_version()
            if "dev" in self.version:
                self.version += str(datetime.now().timestamp())
        return self.version
