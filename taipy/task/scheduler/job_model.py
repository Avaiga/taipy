from dataclasses import dataclass
from typing import NewType

from taipy.task.scheduler.status import Status
from taipy.task.task_entity import TaskId

JobId = NewType("JobId", str)


@dataclass
class JobModel:
    id: JobId
    task_id: TaskId
    status: Status = Status.SUBMITTED
