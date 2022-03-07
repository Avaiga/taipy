import pathlib
from datetime import datetime

from taipy.core.common._utils import _fct_to_dict, _load_fct
from taipy.core.config.config import Config
from taipy.core.job.job import Job
from taipy.core.job.job_model import JobModel
from taipy.core.repository import FileSystemRepository
from taipy.core.task.task_repository import TaskRepository


class JobRepository(FileSystemRepository[JobModel, Job]):
    def __init__(self):
        super().__init__(model=JobModel, dir_name="jobs")

    def to_model(self, job: Job):
        return JobModel(
            job.id,
            job.task.id,
            job.status,
            job.force,
            job.creation_date.isoformat(),
            [],
            self.__serialize_exceptions(job.exceptions),
        )

    def from_model(self, model: JobModel):
        job = Job(id=model.id, task=TaskRepository().load(model.task_id))

        job.status = model.status
        job.force = model.force
        job.creation_date = datetime.fromisoformat(model.creation_date)
        # for it in model.subscribers:
        #     try:
        #         job._subscribers.append(load_fct(it.get("fct_module"), it.get("fct_name")))
        #     except AttributeError:
        #         raise InvalidSubscriber(f"The subscriber function {it.get('fct_name')} cannot be load.")
        job._exceptions = [_load_fct(e["fct_module"], e["fct_name"])(*e["args"]) for e in model.exceptions]

        return job

    @property
    def storage_folder(self) -> pathlib.Path:
        return pathlib.Path(Config.global_config.storage_folder)  # type: ignore

    @staticmethod
    def __serialize_exceptions(exceptions):
        return [{**_fct_to_dict(type(e)), "args": e.args} for e in exceptions]
