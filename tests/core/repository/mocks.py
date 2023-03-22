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
import pathlib
from dataclasses import dataclass
from typing import Any, Dict

from src.taipy.core._repository import _FileSystemRepository, _SQLRepository
from src.taipy.core._repository._v2._abstract_converter import _AbstractConverter
from src.taipy.core._repository._v2._filesystem_repository import _FileSystemRepository as _FileSystemRepositoryV2
from src.taipy.core._version._version_manager import _VersionManager
from taipy.config.config import Config


@dataclass
class MockObj:
    def __init__(self, id: str, name: str, version: str = None) -> None:
        self.id = id
        self.name = name
        if version:
            self.version = version
        else:
            self.version = _VersionManager._get_latest_version()


@dataclass
class MockModel:
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
        return MockModel(id=entity.id, name=entity.name, version=entity.version)


class MockConverter(_AbstractConverter):
    @classmethod
    def _entity_to_model(cls, entity):
        return MockModel(id=entity.id, name=entity.name, version=entity.version)

    @classmethod
    def _model_to_entity(cls, model):
        return MockObj(id=model.id, name=model.name, version=model.version)


class MockFSRepository(_FileSystemRepository):
    def __init__(self, **kwargs):
        kwargs.update({"to_model_fct": self._to_model, "from_model_fct": self._from_model})
        super().__init__(**kwargs)

    def _to_model(self, obj: MockObj):
        return MockModel(obj.id, obj.name, obj.version)

    def _from_model(self, model: MockModel):
        return MockObj(model.id, model.name, model.version)

    @property
    def _storage_folder(self) -> pathlib.Path:
        return pathlib.Path(Config.global_config.storage_folder)  # type: ignore


class MockFSRepositoryV2(_FileSystemRepositoryV2):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def _storage_folder(self) -> pathlib.Path:
        return pathlib.Path(Config.global_config.storage_folder)  # type: ignore


class MockSQLRepository(_SQLRepository):
    def __init__(self, **kwargs):
        kwargs.update({"model_name": "mock_model", "to_model_fct": self._to_model, "from_model_fct": self._from_model})
        super().__init__(**kwargs)

    def _to_model(self, obj: MockObj):
        return MockModel(obj.id, obj.name, obj.version)

    def _from_model(self, model: MockModel):
        return MockObj(model.id, model.name, model.version)
