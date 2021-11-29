from datetime import datetime

from taipy.common.utils import fcts_to_dict, load_fct
from taipy.exceptions import InvalidSubscriber
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
            fcts_to_dict(job._subscribers),
            self.__to_names(job.exceptions),
        )

    def from_model(self, model):
        job = Job(id=model.id, task=TaskRepository(base_path=self.base_path).load(model.task_id))

        job.status = model.status
        job.creation_date = datetime.fromisoformat(model.creation_date) if model.creation_date else None
        for it in model.subscribers:
            try:
                job._subscribers.append(load_fct(it.get("fct_module"), it.get("fct_name")))
            except AttributeError:
                raise InvalidSubscriber(f"The subscriber function {it.get('fct_name')} cannot be load.")
        job.__exceptions = []

        return job

    @staticmethod
    def __to_names(objs):
        return [obj.__name__ for obj in objs]
