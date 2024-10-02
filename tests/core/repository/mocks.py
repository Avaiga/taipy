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

import dataclasses
import pathlib
from dataclasses import dataclass
from typing import Any, Dict, Optional

from taipy.common.config import Config
from taipy.core._repository._abstract_converter import _AbstractConverter
from taipy.core._repository._filesystem_repository import _FileSystemRepository
from taipy.core._version._version_manager import _VersionManager


@dataclass
class MockObj:
    def __init__(self, id: str, name: str, version: Optional[str] = None) -> None:
        self.id = id
        self.name = name
        if version:
            self._version = version
        else:
            self._version = _VersionManager._get_latest_version()


@dataclass
class MockModel:  # type: ignore
    id: str
    name: str
    version: str

    def to_dict(self):
        return dataclasses.asdict(self)

    @staticmethod
    def from_dict(data: Dict[str, Any]):
        return MockModel(id=data["id"], name=data["name"], version=data["version"])

    def _to_entity(self):
        return MockObj(id=self.id, name=self.name, version=self.version)

    @classmethod
    def _from_entity(cls, entity: MockObj):
        return MockModel(id=entity.id, name=entity.name, version=entity._version)

    def to_list(self):
        return [self.id, self.name, self.version]


class MockConverter(_AbstractConverter):
    @classmethod
    def _entity_to_model(cls, entity):
        return MockModel(id=entity.id, name=entity.name, version=entity._version)

    @classmethod
    def _model_to_entity(cls, model):
        return MockObj(id=model.id, name=model.name, version=model.version)


class MockFSRepository(_FileSystemRepository):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def _storage_folder(self) -> pathlib.Path:
        return pathlib.Path(Config.core.storage_folder)  # type: ignore
