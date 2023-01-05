# Copyright 2022 Avaiga Private Limited
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
from typing import Any, Dict, Iterable, List, Optional

from src.taipy.core._manager._manager import _Manager
from src.taipy.core._repository._repository import _AbstractRepository
from src.taipy.core._repository._repository_adapter import _RepositoryAdapter
from src.taipy.core._version._version_manager import _VersionManager
from taipy.config.config import Config


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
            self.version = version
        else:
            self.version = _VersionManager._get_latest_version()


class MockRepository(_AbstractRepository):  # type: ignore
    def __init__(self, **kwargs):
        kwargs.update({"to_model_fct": self._to_model, "from_model_fct": self._from_model})
        self.repo = _RepositoryAdapter.select_base_repository()(**kwargs)

    def _to_model(self, obj: MockEntity):
        return MockModel(obj.id, obj.name, obj.version)

    def _from_model(self, model: MockModel):
        return MockEntity(model.id, model.name, model.version)

    def load(self, model_id: str) -> MockEntity:
        return self.repo.load(model_id)

    def _load_all(self, version_number: Optional[str] = None) -> List[MockEntity]:
        return self.repo._load_all(version_number)

    def _load_all_by(self, by, version_number) -> List[MockEntity]:
        return self.repo._load_all_by(by, version_number)

    def _save(self, entity: MockEntity):
        return self.repo._save(entity)

    def _delete(self, entity_id: str):
        return self.repo._delete(entity_id)

    def _delete_all(self):
        return self.repo._delete_all()

    def _delete_many(self, ids: Iterable[str]):
        return self.repo._delete_many(ids)

    def _search(self, attribute: str, value: Any, version_number: Optional[str] = None) -> Optional[MockEntity]:
        return self.repo._search(attribute, value, version_number)

    @property
    def _storage_folder(self) -> pathlib.Path:
        return pathlib.Path(Config.global_config.storage_folder)  # type: ignore


class MockManager(_Manager[MockEntity]):
    _ENTITY_NAME = MockEntity.__name__
    _repository = MockRepository(model=MockModel, dir_name="foo")


class TestManager:
    def test_save_and_fetch_model(self):
        m = MockEntity("uuid", "foo")
        MockManager._set(m)

        fetched_model = MockManager._get(m.id)
        assert m == fetched_model

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
