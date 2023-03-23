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

import pathlib
from datetime import datetime
from typing import Any, Iterable, List, Optional, Union

from taipy.config import Config

from .._repository._repository import _AbstractRepository
from .._repository._repository_adapter import _RepositoryAdapter
from ._version import _Version
from ._version_model import _VersionModel


class _VersionRepository(_AbstractRepository[_VersionModel, _Version]):  # type: ignore
    _LATEST_VERSION_KEY = "latest_version"
    _DEVELOPMENT_VERSION_KEY = "development_version"
    _PRODUCTION_VERSION_KEY = "production_version"

    def __init__(self, **kwargs):
        kwargs.update({"to_model_fct": self._to_model, "from_model_fct": self._from_model})
        self.repo = _RepositoryAdapter.select_base_repository()(**kwargs)

    @property
    def repository(self):
        return self.repo

    def _to_model(self, version: _Version):
        return _VersionModel(
            id=version.id, config=Config._to_json(version.config), creation_date=version.creation_date.isoformat()
        )

    def _from_model(self, model):
        version = _Version(id=model.id, config=Config._from_json(model.config))
        version.creation_date = datetime.fromisoformat(model.creation_date)
        return version

    def load(self, model_id: str) -> _Version:
        return self.repo.load(model_id)

    def _load_all(self, version_number: Optional[str] = "all") -> List[_Version]:
        return self.repo._load_all(version_number)

    def _load_all_by(self, by, version_number: Optional[str] = "all") -> List[_Version]:
        return self.repo._load_all_by(by, version_number)

    def _save(self, entity: _Version):
        return self.repo._save(entity)

    def _delete(self, entity_id: str):
        return self.repo._delete(entity_id)

    def _delete_all(self):
        return self.repo._delete_all()

    def _delete_many(self, ids: Iterable[str]):
        return self.repo._delete_many(ids)

    def _delete_by(self, attribute: str, value: str, version_number: Optional[str] = None):
        return self.repo._delete_by(attribute, value, version_number)

    def _search(self, attribute: str, value: Any, version_number: Optional[str] = None) -> Optional[_Version]:
        return self.repo._search(attribute, value, version_number)

    def _export(self, entity_id: str, folder_path: Union[str, pathlib.Path]):
        return self.repo._export(entity_id, folder_path)

    def _set_latest_version(self, version_number):
        self.repo._set_latest_version(version_number)

    def _get_latest_version(self) -> str:
        return self.repo._get_latest_version()

    def _set_development_version(self, version_number):
        self.repo._set_development_version(version_number)

    def _get_development_version(self) -> str:
        return self.repo._get_development_version()

    def _set_production_version(self, version_number):
        self.repo._set_production_version(version_number)

    def _get_production_versions(self) -> List[str]:
        return self.repo._get_production_versions()

    def _delete_production_version(self, version_number):
        self.repo._delete_production_version(version_number)
