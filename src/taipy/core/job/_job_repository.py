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

import pathlib
from datetime import datetime
from typing import List

from taipy.config.config import Config
from taipy.logger._taipy_logger import _TaipyLogger

from ._job_model import _JobModel
from .job import Job
from .._repository import _FileSystemRepository
from ..common._utils import _fcts_to_dict, _load_fct
from ..exceptions.exceptions import InvalidSubscriber
from ..task._task_repository import _TaskRepository


class _JobRepository(_FileSystemRepository[_JobModel, Job]):
    __logger = _TaipyLogger._get_logger()

    def __init__(self):
        super().__init__(model=_JobModel, dir_name="jobs")

    def _to_model(self, job: Job):
        return _JobModel(
            job.id,
            job._task.id,
            job._status,
            job._force,
            job._creation_date.isoformat(),
            self._serialize_subscribers(job._subscribers),
            job._stacktrace,
        )

    def _from_model(self, model: _JobModel):
        job = Job(id=model.id, task=_TaskRepository().load(model.task_id))

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

    @property
    def _storage_folder(self) -> pathlib.Path:
        return pathlib.Path(Config.global_config.storage_folder)  # type: ignore

    @staticmethod
    def _serialize_subscribers(subscribers: List) -> List:
        return _fcts_to_dict(subscribers)
