__all__ = ["TaskScheduler"]

import uuid
from concurrent.futures import ThreadPoolExecutor
from typing import Dict

from taipy.task.task_entity import TaskEntity

from .executor import FutureExecutor
from .job import Job, JobId


class TaskScheduler:
    """
    Create and schedule Jobs from Task and keep their states
    """

    def __init__(self, parallel_execution=False):
        self.__jobs: Dict[JobId, Job] = {}
        self.__executor = (
            FutureExecutor() if not parallel_execution else ThreadPoolExecutor()
        )

    def submit(self, task: TaskEntity) -> JobId:
        """
        Submit a task that should be executed as a Job
        """
        self.__executor.submit(
            self.__execute_function_and_write_outputs,
            task.function,
            task.input,
            task.output,
        )
        return self.__create_job(task)

    def __create_job(self, task: TaskEntity) -> JobId:
        job = Job(id=JobId(f"job_id_{task.id}_{uuid.uuid4()}"), task_id=task.id)
        self.__jobs[job.id] = job
        return job.id

    @staticmethod
    def __execute_function_and_write_outputs(function, inputs, outputs):
        r = function(*[i.get() for i in inputs])
        for o in outputs:
            o.write(r)
