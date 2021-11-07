from taipy.repository import FileSystemRepository
from taipy.task import Job
from taipy.task.scheduler.job_model import JobModel


class JobRepository(FileSystemRepository[JobModel, Job]):
    def to_model(self, job):
        pass

    def from_model(self, model):
        pass
