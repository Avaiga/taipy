from dataclasses import dataclass
from typing import Callable, List

from dataclasses_json import dataclass_json

from taipy.common.alias import Datetime, JobId
from taipy.task import Status


@dataclass_json
@dataclass
class JobModel:
    id: JobId
    task_id: str
    status: Status
    creation_date: Datetime
    subscribers: List[str]
    exceptions: List[str]
