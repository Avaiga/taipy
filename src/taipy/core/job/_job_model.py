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
from typing import Any, Dict, List

from .._version._utils import _version_migration
from ..common._utils import _fcts_to_dict, _load_fct
from ..common.alias import JobId
from ..exceptions import InvalidSubscriber
from ..job.job import Job
from ..task._task_repository_factory import _TaskRepositoryFactory
from .status import Status


@dataclass
class _JobModel:
    id: JobId
    task_id: str
    status: Status
    force: bool
    submit_id: str
    creation_date: str
    subscribers: List[Dict]
    stacktrace: List[str]
    version: str

    def to_dict(self) -> Dict[str, Any]:
        return {**dataclasses.asdict(self), "status": repr(self.status)}

    @staticmethod
    def from_dict(data: Dict[str, Any]):
        return _JobModel(
            id=data["id"],
            task_id=data["task_id"],
            status=Status._from_repr(data["status"]),
            force=data["force"],
            submit_id=data["submit_id"],
            creation_date=data["creation_date"],
            subscribers=data["subscribers"],
            stacktrace=data["stacktrace"],
            version=data["version"] if "version" in data.keys() else _version_migration(),
        )

    def _to_entity(self):
        task_repository = _TaskRepositoryFactory._build_repository()
        job = Job(id=self.id, task=task_repository.load(self.task_id), submit_id=self.submit_id, version=self.version)

        job.status = self.status  # type: ignore
        job.force = self.force  # type: ignore
        job.creation_date = datetime.fromisoformat(self.creation_date)  # type: ignore
        for it in self.subscribers:
            try:
                job._subscribers.append(_load_fct(it.get("fct_module"), it.get("fct_name")))  # type:ignore
            except AttributeError:
                raise InvalidSubscriber(f"The subscriber function {it.get('fct_name')} cannot be loaded.")
        job._stacktrace = self.stacktrace

        return job

    @classmethod
    def _from_entity(self, job: Job) -> "_JobModel":
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

    @staticmethod
    def _serialize_subscribers(subscribers: List) -> List:
        return _fcts_to_dict(subscribers)
