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

from datetime import datetime
from typing import List

from .._repository._abstract_converter import _AbstractConverter
from ..common._utils import _fcts_to_dict, _load_fct
from ..exceptions import InvalidSubscriber
from ..job._job_model import _JobModel
from ..job.job import Job
from ..task._task_manager_factory import _TaskManagerFactory


class _JobConverter(_AbstractConverter):
    @classmethod
    def _entity_to_model(cls, job: Job) -> _JobModel:
        return _JobModel(
            job.id,
            job._task.id,
            job._status,
            {status: timestamp.isoformat() for status, timestamp in job._status_change_records.items()},
            job._force,
            job.submit_id,
            job.submit_entity_id,
            job._creation_date.isoformat(),
            cls.__serialize_subscribers(job._subscribers),
            job._stacktrace,
            version=job._version,
        )

    @classmethod
    def _model_to_entity(cls, model: _JobModel) -> Job:
        task_manager = _TaskManagerFactory._build_manager()
        task_repository = task_manager._repository

        job = Job(
            id=model.id,
            task=task_repository._load(model.task_id),
            submit_id=model.submit_id,
            submit_entity_id=model.submit_entity_id,
            version=model.version,
        )

        job._status = model.status  # type: ignore
        job._status_change_records = {
            status: datetime.fromisoformat(timestamp) for status, timestamp in model.status_change_records.items()
        }
        job._force = model.force  # type: ignore
        job._creation_date = datetime.fromisoformat(model.creation_date)  # type: ignore
        for it in model.subscribers:
            try:
                fct_module, fct_name = it.get("fct_module"), it.get("fct_name")
                job._subscribers.append(_load_fct(fct_module, fct_name))  # type: ignore
            except AttributeError:
                raise InvalidSubscriber(f"The subscriber function {it.get('fct_name')} cannot be loaded.") from None
        job._stacktrace = model.stacktrace

        return job

    @staticmethod
    def __serialize_subscribers(subscribers: List) -> List:
        return _fcts_to_dict(subscribers)
