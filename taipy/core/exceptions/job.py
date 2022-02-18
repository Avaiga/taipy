class JobNotDeletedException(RuntimeError):
    """
    Raised if we try to delete a job that cannot be deleted.
    """

    def __init__(self, job_id: str):
        self.message = f"Job: {job_id} cannot be deleted."


class NonExistingJob(RuntimeError):
    """
    Raised if we try to get a job that does not exist.
    """

    def __init__(self, job_id: str):
        self.message = f"Job: {job_id} does not exist."


class DataNodeWritingError(RuntimeError):
    """
    Raised if an error happens during the writing in a data node.
    """

    pass


class InvalidSubscriber(RuntimeError):
    """
    Raised if we try to load a function that is not valid.
    """

    pass
