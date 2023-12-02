# Copyright 2023 Avaiga Private Limited
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
from copy import copy

from taipy.config import Config as TaipyConfig
from taipy.config import UniqueSection

from ._default_config import default_config


class _GuiSection(UniqueSection):
    name = "gui"

    def __init__(self, property_list: t.Optional[t.List] = None, **properties):
        self._property_list = property_list
        super().__init__(**properties)

    def __copy__(self):
        return _GuiSection(property_list=copy(self._property_list), **copy(self._properties))

    def _clean(self):
        self._properties.clear()

    def _to_dict(self):
        as_dict = {}
        as_dict.update(self._properties)
        return as_dict

    @classmethod
    def _from_dict(cls, as_dict: t.Dict[str, t.Any], *_):
        return _GuiSection(property_list=list(default_config), **as_dict)

    def _update(self, as_dict: t.Dict[str, t.Any]):
        if self._property_list:
            as_dict = {k: v for k, v in as_dict.items() if k in self._property_list}
        self._properties.update(as_dict)

    @staticmethod
    def _configure(**properties) -> "_GuiSection":
        """NOT DOCUMENTED
        Configure the Graphical User Interface.

        Parameters:
            **properties (dict[str, any]): Keyword arguments that configure the behavior of the `Gui^` instances.<br/>
                Please refer to the
                [Configuration section](../gui/configuration.md#configuring-the-gui-instance)
                of the User Manual for more information on the accepted arguments.
        Returns:
            The GUI configuration.

        """
        section = _GuiSection(property_list=list(default_config), **properties)
        TaipyConfig._register(section)
        return TaipyConfig.unique_sections[_GuiSection.name]
