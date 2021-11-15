from datetime import datetime
from importlib import import_module

from taipy.repository import FileSystemRepository
from taipy.task import Job
from taipy.task.repository import TaskRepository
from taipy.task.scheduler.job_model import JobModel


class JobRepository(FileSystemRepository[JobModel, Job]):
    def to_model(self, job):
        return JobModel(
            job.id,
            job.task.id,
            job.status,
            job.creation_date.isoformat(),
            self.__to_dict(job._subscribers),
            self.__to_names(job.exceptions),
        )

    def from_model(self, model):
        job = Job(id=model.id, task=TaskRepository(base_path=self.base_path).load(model.task_id))

        job.status = model.status
        job.creation_date = datetime.fromisoformat(model.creation_date) if model.creation_date else None
        job._subscribers = [self.__load_fct(it.get("fct_module"), it.get("fct_name")) for it in model.subscribers]
        job.__exceptions = []

        return job

    @staticmethod
    def __to_names(objs):
        return [obj.__name__ for obj in objs]

    @staticmethod
    def __to_dict(objs):
        return [{"fct_name": obj.__name__, "fct_module": obj.__module__} for obj in objs]

    @staticmethod
    def __load_fct(module_name, fct_name):
        module = import_module(module_name)
        return getattr(module, fct_name)
