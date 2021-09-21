from typing import List

from taipy.pipeline import Pipeline


class Scenario:
    def __init__(self, name: str, pipelines: List[Pipeline], **properties):
        self.name = name
        self.pipelines = pipelines
        self.properties = properties
