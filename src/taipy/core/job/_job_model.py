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
from dataclasses import dataclass
from typing import Any, Dict, List

from sqlalchemy import JSON, Boolean, Column, Enum, String, Table

from .._repository._base_taipy_model import _BaseModel
from .._repository.db._sql_base_model import mapper_registry
from .job_id import JobId
from .status import Status


@mapper_registry.mapped
@dataclass
class _JobModel(_BaseModel):
    __table__ = Table(
        "job",
        mapper_registry.metadata,
        Column("id", String, primary_key=True),
        Column("task_id", String),
        Column("status", Enum(Status)),
        Column("force", Boolean),
        Column("submit_id", String),
        Column("submit_entity_id", String),
        Column("creation_date", String),
        Column("subscribers", JSON),
        Column("stacktrace", JSON),
        Column("version", String),
    )
    id: JobId
    task_id: str
    status: Status
    force: bool
    submit_id: str
    submit_entity_id: str
    creation_date: str
    subscribers: List[Dict]
    stacktrace: List[str]
    version: str

    @staticmethod
    def from_dict(data: Dict[str, Any]):
        return _JobModel(
            id=data["id"],
            task_id=data["task_id"],
            status=Status._from_repr(data["status"]),
            force=data["force"],
            submit_id=data["submit_id"],
            submit_entity_id=data["submit_entity_id"],
            creation_date=data["creation_date"],
            subscribers=data["subscribers"],
            stacktrace=data["stacktrace"],
            version=data["version"],
        )
