from taipy.common.alias import JobId, TaskId
from taipy.task import Job, Task
from taipy.task.repository import TaskRepository
from taipy.task.scheduler.job_model import JobModel
from taipy.task.scheduler.job_repository import JobRepository


def test_save_and_load_job(tmpdir):
    t_id = TaskId("task_1")
    t = Task("name_1", [], print, [], t_id)
    TaskRepository(base_path=tmpdir).save(t)

    j_id = JobId("job_1")
    j = Job(id=j_id, task=t)
    j.on_status_change(print)
    r = JobRepository(model=JobModel, dir_name="jobs", base_path=tmpdir)
    r.save(j)
    job = r.load(j_id)

    assert job == j
