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
from typing import Any, Iterable, List, Optional, Union

from .._repository._repository import _AbstractRepository
from .._repository._repository_adapter import _RepositoryAdapter
from ._job_model import _JobModel
from .job import Job


class _JobRepository(_AbstractRepository[_JobModel, Job]):  # type: ignore
    def __init__(self, **kwargs):
        kwargs.update({"to_model_fct": Job._to_model, "from_model_fct": Job._from_model})
        self.repo = _RepositoryAdapter.select_base_repository()(**kwargs)

    @property
    def repository(self):
        return self.repo

    def load(self, model_id: str) -> Job:
        return self.repo.load(model_id)

    def _load_all(self, version_number: Optional[str] = None) -> List[Job]:
        return self.repo._load_all(version_number)

    def _load_all_by(self, by, version_number: Optional[str] = None) -> List[Job]:
        return self.repo._load_all_by(by, version_number)

    def _save(self, entity: Job):
        return self.repo._save(entity)

    def _delete(self, entity_id: str):
        return self.repo._delete(entity_id)

    def _delete_all(self):
        return self.repo._delete_all()

    def _delete_many(self, ids: Iterable[str]):
        return self.repo._delete_many(ids)

    def _delete_by(self, attribute: str, value: str, version_number: Optional[str] = None):
        return self.repo._delete_by(attribute, value, version_number)

    def _search(self, attribute: str, value: Any, version_number: Optional[str] = None) -> Optional[Job]:
        return self.repo._search(attribute, value, version_number)

    def _export(self, entity_id: str, folder_path: Union[str, pathlib.Path]):
        return self.repo._export(entity_id, folder_path)
