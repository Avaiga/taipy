from dataclasses import dataclass
from typing import Dict, List

from dataclasses_json import dataclass_json

from taipy.common.alias import JobId
from taipy.task import Status


@dataclass_json
@dataclass
class JobModel:
    id: JobId
    task_id: str
    status: Status
    creation_date: str
    subscribers: List[Dict]
    exceptions: List[str]
