from typing import List

from taipy.pipeline import Pipeline


class Scenario:
    def __init__(self, name: str, pipelines: List[Pipeline], **properties):
        self.name = name.strip().lower().replace(' ', '_')
        self.pipelines = pipelines
        self.properties = properties
