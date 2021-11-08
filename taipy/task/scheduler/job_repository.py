from taipy.repository import FileSystemRepository
from taipy.task import Job
from taipy.task.manager import TaskManager
from taipy.task.scheduler.job_model import JobModel


class JobRepository(FileSystemRepository[JobModel, Job]):
    def to_model(self, job):
        return JobModel(
            job.id,
            job.task.id,
            job.status,
            job.creation_date,
            self.__to_names(job._subscribers),
            self.__to_names(job.exceptions),
        )

    def from_model(self, model):
        job = Job(id=model.id, task=TaskManager().get(model.task_id))

        job.status = model.status
        job.creation_date = model.creation_date
        job._subscribers = self.__to_objs(model.subscribers)
        job.__exceptions = []

        return job

    @staticmethod
    def __to_names(objs):
        return [obj.__name__ for obj in objs]

    @staticmethod
    def __to_objs(names):
        return [locals()[name] for name in names]
