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

from .._repository._base_taipy_model import _BaseModel


@dataclass
class _VersionModel(_BaseModel):
    id: str
    config: str
    creation_date: str

    @staticmethod
    def from_dict(data: Dict[str, Any]):
        model = _VersionModel(
            id=data["id"],
            config=data["config"],
            creation_date=data["creation_date"],
        )
        return model

    def to_list(self):
        return [self.id, self.config, self.creation_date]
