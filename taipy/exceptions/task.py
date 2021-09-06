class NonExistingTask(Exception):
    """
    Exception raised if we request a task not known by the task manager.
    """
    def __init__(self, task_id: str):
        ...
        self.task_id = task_id
        self.message = f"Task : {task_id} does not exist."
