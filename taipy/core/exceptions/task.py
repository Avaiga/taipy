class NonExistingTask(Exception):
    """
    Raised when a requested task is not known by the Task Manager.
    """

    def __init__(self, task_id: str):
        self.message = f"Task: {task_id} does not exist."


class NonExistingTaskConfig(Exception):
    """
    Raised when a requested task configuration is not known by the Task Manager.
    """

    def __init__(self, id: str):
        self.message = f"Task config: {id} does not exist."


class MultipleTaskFromSameConfigWithSameParent(Exception):
    """
    Raised if there are multiple tasks from the same task configuration and the same parent identifier.
    """

    pass
