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
from dataclasses import dataclass
from datetime import date, datetime

from taipy.core import Scenario
from taipy.gui.gui import _DoNotUpdate


@dataclass
class _Filter(_DoNotUpdate):
    label: str
    property_type: t.Optional[t.Type]

    def get_property(self):
        return self.label

    def get_type(self):
        if self.property_type is bool:
            return "boolean"
        elif self.property_type is int or self.property_type is float:
            return "number"
        elif self.property_type is datetime or self.property_type is date:
            return "date"
        elif self.property_type is str:
            return "str"
        return "any"


@dataclass
class ScenarioFilter(_Filter):
    """
    used to describe a filter on a scenario property
    """

    property_id: str

    def get_property(self):
        return self.property_id


@dataclass
class DataNodeScenarioFilter(_Filter):
    """
    used to describe a filter on a scenario datanode's property
    """

    datanode_config_id: str
    property_id: str

    def get_property(self):
        return f"{self.datanode_config_id}.{self.property_id}"


_CUSTOM_PREFIX = "fn:"


@dataclass
class CustomScenarioFilter(_Filter):
    """
    used to describe a custom scenario filter ie based on a user defined function
    """

    filter_function: t.Callable[[Scenario], t.Any]

    def __post_init__(self):
        if self.filter_function.__name__ == "<lambda>":
            raise TypeError("CustomScenarioFilter does not support lambda functions.")
        mod = self.filter_function.__module__
        self.module = mod if isinstance(mod, str) else mod.__name__

    def get_property(self):
        return f"{_CUSTOM_PREFIX}{self.module}:{self.filter_function.__name__}"

    @staticmethod
    def _get_custom(col: str) -> t.Optional[t.List[str]]:
        return col[len(_CUSTOM_PREFIX) :].split(":") if col.startswith(_CUSTOM_PREFIX) else None


@dataclass
class DataNodeFilter(_Filter):
    """
    used to describe a filter on a datanode property
    """

    property_id: str

    def get_property(self):
        return self.property_id
