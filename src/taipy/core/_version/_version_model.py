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

import dataclasses
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict

from taipy.config import Config

from .._version._version import _Version


@dataclass
class _VersionModel:
    id: str
    config: Dict[str, Any]
    creation_date: str

    def to_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)

    @staticmethod
    def from_dict(data: Dict[str, Any]):
        return _VersionModel(
            id=data["id"],
            config=data["config"],
            creation_date=data["creation_date"],
        )

    def _to_entity(self):
        version = _Version(id=self.id, config=Config._from_json(self.config))
        version.creation_date = datetime.fromisoformat(self.creation_date)
        return version

    @classmethod
    def _from_entity(cls, version: _Version) -> "_VersionModel":
        return _VersionModel(
            id=version.id, config=Config._to_json(version.config), creation_date=version.creation_date.isoformat()
        )
