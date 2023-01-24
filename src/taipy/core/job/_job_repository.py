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

from taipy.logger._taipy_logger import _TaipyLogger

from .._repository._repository import _AbstractRepository
from .._repository._repository_adapter import _RepositoryAdapter
from ..common._utils import _fcts_to_dict, _load_fct
from ..exceptions.exceptions import InvalidSubscriber
from ..task._task_repository_factory import _TaskRepositoryFactory
from ._job_model import _JobModel
from .job import Job


class _JobRepository(_AbstractRepository[_JobModel, Job]):  # type: ignore
    __logger = _TaipyLogger._get_logger()

    def __init__(self, **kwargs):
        kwargs.update({"to_model_fct": self._to_model, "from_model_fct": self._from_model})
        self.repo = _RepositoryAdapter.select_base_repository()(**kwargs)

    @property
    def repository(self):
        return self.repo

    def _to_model(self, job: Job):
        return _JobModel(
            job.id,
            job._task.id,
            job._status,
            job._force,
            job.submit_id,
            job._creation_date.isoformat(),
            self._serialize_subscribers(job._subscribers),
            job._stacktrace,
            version=job.version,
        )

    def _from_model(self, model: _JobModel):
        task_repository = _TaskRepositoryFactory._build_repository()
        job = Job(
            id=model.id, task=task_repository.load(model.task_id), submit_id=model.submit_id, version=model.version
        )

        job.status = model.status  # type: ignore
        job.force = model.force  # type: ignore
        job.creation_date = datetime.fromisoformat(model.creation_date)  # type: ignore
        for it in model.subscribers:
            try:
                job._subscribers.append(_load_fct(it.get("fct_module"), it.get("fct_name")))  # type:ignore
            except AttributeError:
                raise InvalidSubscriber(f"The subscriber function {it.get('fct_name')} cannot be loaded.")
        job._stacktrace = model.stacktrace

        return job

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

    @staticmethod
    def _serialize_subscribers(subscribers: List) -> List:
        return _fcts_to_dict(subscribers)
