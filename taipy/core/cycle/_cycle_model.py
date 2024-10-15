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

from dataclasses import dataclass
from typing import Any, Dict

from taipy.common.config.common.frequency import Frequency

from .._repository._base_taipy_model import _BaseModel
from .cycle_id import CycleId


@dataclass
class _CycleModel(_BaseModel):
    id: CycleId
    name: str
    frequency: Frequency
    properties: Dict[str, Any]
    creation_date: str
    start_date: str
    end_date: str

    @staticmethod
    def from_dict(data: Dict[str, Any]):
        return _CycleModel(
            id=data["id"],
            name=data["name"],
            frequency=Frequency._from_repr(data["frequency"]),
            properties=_BaseModel._deserialize_attribute(data["properties"]),
            creation_date=data["creation_date"],
            start_date=data["start_date"],
            end_date=data["end_date"],
        )

    def to_list(self):
        return [
            self.id,
            self.name,
            repr(self.frequency),
            _BaseModel._serialize_attribute(self.properties),
            self.creation_date,
            self.start_date,
            self.end_date,
        ]
