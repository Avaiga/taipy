import pathlib
from datetime import datetime

from taipy.config.config import Config
from taipy.job.job import Job
from taipy.job.job_model import JobModel
from taipy.repository import FileSystemRepository
from taipy.task.task_repository import TaskRepository


class JobRepository(FileSystemRepository[JobModel, Job]):
    def __init__(self):
        super().__init__(model=JobModel, dir_name="jobs")

    def to_model(self, job):
        return JobModel(
            job.id,
            job.task.id,
            job.status,
            job.creation_date.isoformat(),
            [],
            self.__to_names(job.exceptions),
        )

    def from_model(self, model):
        job = Job(id=model.id, task=TaskRepository().load(model.task_id))

        job.status = model.status
        job.creation_date = datetime.fromisoformat(model.creation_date) if model.creation_date else None
        # for it in model.subscribers:
        #     try:
        #         job._subscribers.append(load_fct(it.get("fct_module"), it.get("fct_name")))
        #     except AttributeError:
        #         raise InvalidSubscriber(f"The subscriber function {it.get('fct_name')} cannot be load.")
        job.__exceptions = []

        return job

    @property
    def storage_folder(self) -> pathlib.Path:
        return pathlib.Path(Config.global_config().storage_folder)  # type: ignore

    @staticmethod
    def __to_names(objs):
        return [obj.__name__ for obj in objs]
