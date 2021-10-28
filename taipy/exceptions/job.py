class JobNotDeletedException(RuntimeError):
    """
    Exception raised if we try to delete a job that cannot be deleted.
    """

    def __init__(self, job_id: str):
        self.message = f"Job : {job_id} cannot be deleted."


class NonExistingJob(RuntimeError):
    """
    Exception raised if we try to get a job that does not exist.
    """

    def __init__(self, job_id: str):
        self.message = f"Job : {job_id} does not exist."


class DataSourceWritingError(RuntimeError):
    """
    Exception raised if an error happen during the writing in a datasource
    """

    pass
