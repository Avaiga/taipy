from taipy.task import TaskId
from taipy.task.scheduler.job import Job, JobId


def test_create_job():
    job_id = JobId("id1")
    task_id = TaskId("task_id1")

    job = Job(job_id, task_id)

    assert job.id == job_id
    assert job.task_id == task_id
