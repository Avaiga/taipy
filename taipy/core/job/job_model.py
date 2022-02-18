import dataclasses
from dataclasses import dataclass
from typing import Any, Dict, List

from taipy.core.common.alias import JobId
from taipy.core.job.status import Status


@dataclass
class JobModel:
    id: JobId
    task_id: str
    status: Status
    force: bool
    creation_date: str
    subscribers: List[Dict]
    exceptions: List[Dict]

    def to_dict(self) -> Dict[str, Any]:
        return {**dataclasses.asdict(self), "status": repr(self.status)}

    @staticmethod
    def from_dict(data: Dict[str, Any]):
        return JobModel(
            id=data["id"],
            task_id=data["task_id"],
            status=Status.from_repr(data["status"]),
            force=data["force"],
            creation_date=data["creation_date"],
            subscribers=data["subscribers"],
            exceptions=data["exceptions"],
        )
