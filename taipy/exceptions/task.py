class NonExistingTaskEntity(Exception):
    """
    Exception raised if we request a task entity not known by the task manager.
    """

    def __init__(self, task_id: str):
        self.message = f"Task entity : {task_id} does not exist."


class NonExistingTask(Exception):
    """
    Exception raised if we request a task not known by the task manager.
    """

    def __init__(self, name: str):
        self.message = f"Task : {name} does not exist."
