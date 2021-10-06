from typing import List

from taipy.task import TaskConfig


class PipelineConfig:
    def __init__(self, name: str, tasks: List[TaskConfig], **properties):
        self.name = name.strip().lower().replace(' ', '_')
        self.tasks = tasks
        self.properties = properties
