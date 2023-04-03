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
from typing import Any, Dict, List

from .._version._utils import _version_migration
from .job_id import JobId
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
