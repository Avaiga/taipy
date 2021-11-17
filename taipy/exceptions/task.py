class NonExistingTask(Exception):
    """
    Exception raised if we request a task not known by the task manager.
    """

    def __init__(self, task_id: str):
        self.message = f"Task : {task_id} does not exist."


class NonExistingTaskConfig(Exception):
    """
    Exception raised if we request a task config not known by the task manager.
    """

    def __init__(self, name: str):
        self.message = f"Task config : {name} does not exist."


class MultipleTaskFromSameConfigWithSameParent(Exception):
    """
    Exception raised if it exists multiple tasks from the same task config and with the same parent_id
    """

    pass
