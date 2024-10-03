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

from dataclasses import dataclass
from typing import Any, Dict, List

from .._repository._base_taipy_model import _BaseModel
from .job_id import JobId
from .status import Status


@dataclass
class _JobModel(_BaseModel):
    id: JobId
    task_id: str
    status: Status
    status_change_records: Dict[str, str]
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
            status_change_records=_BaseModel._deserialize_attribute(data["status_change_records"]),
            force=data["force"],
            submit_id=data["submit_id"],
            submit_entity_id=data["submit_entity_id"],
            creation_date=data["creation_date"],
            subscribers=_BaseModel._deserialize_attribute(data["subscribers"]),
            stacktrace=_BaseModel._deserialize_attribute(data["stacktrace"]),
            version=data["version"],
        )

    def to_list(self):
        return [
            self.id,
            self.task_id,
            repr(self.status),
            _BaseModel._serialize_attribute(self.status_change_records),
            self.force,
            self.submit_id,
            self.submit_entity_id,
            self.creation_date,
            _BaseModel._serialize_attribute(self.subscribers),
            _BaseModel._serialize_attribute(self.stacktrace),
            self.version,
        ]
