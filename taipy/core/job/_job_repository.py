import pathlib
from datetime import datetime

from taipy.core._repository import _FileSystemRepository
from taipy.core.common._utils import _fct_to_dict, _load_fct
from taipy.core.config.config import Config
from taipy.core.job._job_model import _JobModel
from taipy.core.job.job import Job
from taipy.core.task._task_repository import _TaskRepository


class _JobRepository(_FileSystemRepository[_JobModel, Job]):
    def __init__(self):
        super().__init__(model=_JobModel, dir_name="jobs")

    def _to_model(self, job: Job):
        return _JobModel(
            job.id,
            job._task.id,
            job._status,
            job._force,
            job._creation_date.isoformat(),
            [],
            self.__serialize_exceptions(job.exceptions),
        )

    def _from_model(self, model: _JobModel):
        job = Job(id=model.id, task=_TaskRepository().load(model.task_id))

        job.status = model.status  # type: ignore
        job.force = model.force  # type: ignore
        job.creation_date = datetime.fromisoformat(model.creation_date)  # type: ignore
        # for it in model.subscribers:
        #     try:
        #         job._subscribers.append(load_fct(it.get("fct_module"), it.get("fct_name")))
        #     except AttributeError:
        #         raise InvalidSubscriber(f"The subscriber function {it.get('fct_name')} cannot be load.")
        job._exceptions = [_load_fct(e["fct_module"], e["fct_name"])(*e["args"]) for e in model.exceptions]

        return job

    @property
    def _storage_folder(self) -> pathlib.Path:
        return pathlib.Path(Config.global_config.storage_folder)  # type: ignore

    @staticmethod
    def __serialize_exceptions(exceptions):
        return [{**_fct_to_dict(type(e)), "args": e.args} for e in exceptions]
