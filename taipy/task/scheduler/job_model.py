from dataclasses import dataclass
from typing import Callable, List

from dataclasses_json import dataclass_json

from taipy.common.alias import Datetime, JobId
from taipy.task import Status, Task


@dataclass_json
@dataclass
class JobModel:
    id: JobId
    task: Task
    status: Status
    creation_date: Datetime
    subscribers: List[Callable]
    exceptions: List[Exception]
