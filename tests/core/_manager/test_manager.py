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
from typing import Any, Dict, Iterable, List, Optional, Union

from taipy.common.config.config import Config
from taipy.core._manager._manager import _Manager
from taipy.core._repository._abstract_converter import _AbstractConverter
from taipy.core._repository._abstract_repository import _AbstractRepository
from taipy.core._repository._filesystem_repository import _FileSystemRepository
from taipy.core._version._version_manager import _VersionManager


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


@dataclass
class MockEntity:
    def __init__(self, id: str, name: str, version: str = None) -> None:
        self.id = id
        self.name = name
        if version:
            self._version = version
        else:
            self._version = _VersionManager._get_latest_version()


class MockConverter(_AbstractConverter):
    @classmethod
    def _entity_to_model(cls, entity: MockEntity) -> MockModel:
        return MockModel(id=entity.id, name=entity.name, version=entity._version)

    @classmethod
    def _model_to_entity(cls, model: MockModel) -> MockEntity:
        return MockEntity(id=model.id, name=model.name, version=model.version)


class MockRepository(_AbstractRepository):  # type: ignore
    def __init__(self, **kwargs):
        self.repo = _FileSystemRepository(**kwargs, converter=MockConverter)

    def _to_model(self, obj: MockEntity):
        return MockModel(obj.id, obj.name, obj._version)

    def _from_model(self, model: MockModel):
        return MockEntity(model.id, model.name, model.version)

    def _load(self, entity_id: str) -> MockEntity:
        return self.repo._load(entity_id)

    def _load_all(self, filters: Optional[List[Dict]] = None) -> List[MockEntity]:
        return self.repo._load_all(filters)

    def _save(self, entity: MockEntity):
        return self.repo._save(entity)

    def _exists(self, entity_id: str) -> bool:
        return self.repo._exists(entity_id)

    def _delete(self, entity_id: str):
        return self.repo._delete(entity_id)

    def _delete_all(self):
        return self.repo._delete_all()

    def _delete_many(self, ids: Iterable[str]):
        return self.repo._delete_many(ids)

    def _delete_by(self, attribute: str, value: str):
        return self.repo._delete_by(attribute, value)

    def _search(self, attribute: str, value: Any, filters: Optional[List[Dict]] = None) -> List[MockEntity]:
        return self.repo._search(attribute, value, filters)

    def _export(self, entity_id: str, folder_path: Union[str, pathlib.Path]):
        return self.repo._export(self, entity_id, folder_path)

    @property
    def _storage_folder(self) -> pathlib.Path:
        return pathlib.Path(Config.core.storage_folder)  # type: ignore


class MockManager(_Manager[MockEntity]):
    _ENTITY_NAME = MockEntity.__name__
    _repository = MockRepository(model_type=MockModel, dir_name="foo")


class TestManager:
    def test_save_and_fetch_model(self):
        m = MockEntity("uuid", "foo")
        MockManager._set(m)

        fetched_model = MockManager._get(m.id)
        assert m == fetched_model

    def test_exists(self):
        m = MockEntity("uuid", "foo")
        MockManager._set(m)
        assert MockManager._exists(m.id)

    def test_get(self):
        m = MockEntity("uuid", "foo")
        MockManager._set(m)
        assert MockManager._get(m.id) == m

    def test_get_all(self):
        MockManager._delete_all()

        objs = []
        for i in range(5):
            m = MockEntity(f"uuid-{i}", f"Foo{i}")
            objs.append(m)
            MockManager._set(m)
        _objs = MockManager._get_all()

        assert len(_objs) == 5

    def test_delete(self):
        m = MockEntity("uuid", "foo")
        MockManager._set(m)
        MockManager._delete(m.id)
        assert MockManager._get(m.id) is None

    def test_delete_all(self):
        objs = []
        for i in range(5):
            m = MockEntity(f"uuid-{i}", f"Foo{i}")
            objs.append(m)
            MockManager._set(m)
        MockManager._delete_all()
        assert MockManager._get_all() == []

    def test_delete_many(self):
        objs = []
        for i in range(5):
            m = MockEntity(f"uuid-{i}", f"Foo{i}")
            objs.append(m)
            MockManager._set(m)
        MockManager._delete_many(["uuid-0", "uuid-1"])
        assert len(MockManager._get_all()) == 3

    def test_is_editable(self):
        m = MockEntity("uuid", "Foo")
        MockManager._set(m)
        assert MockManager._is_editable(m)

        rc = MockManager._is_editable("some_entity")
        assert not rc
        assert "Entity some_entity does not exist in the repository." in rc.reasons

    def test_is_readable(self):
        m = MockEntity("uuid", "Foo")
        MockManager._set(m)
        assert MockManager._is_readable(m)

        rc = MockManager._is_editable("some_entity")
        assert not rc
        assert "Entity some_entity does not exist in the repository." in rc.reasons
