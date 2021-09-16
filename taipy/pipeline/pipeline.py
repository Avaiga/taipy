from typing import List

from taipy.task import Task


class Pipeline:
    def __init__(self, name: str, tasks: List[Task], **properties):
        self.name = name
        self.tasks = tasks
        self.properties = properties
