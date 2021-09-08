import logging

from taipy.task import Task
from .job import JobId


class TaskScheduler:

    def __init__(self, **kwargs):
        pass

    def submit(self, task: Task):
        job_id = JobId("job_id_" + task.id)
        logging.info(f"task {task.id} submitted. Job id : {job_id}")
