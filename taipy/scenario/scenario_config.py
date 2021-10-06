from typing import List

from taipy.pipeline import PipelineConfig


class ScenarioConfig:
    def __init__(self, name: str, pipelines: List[PipelineConfig], **properties):
        self.name = name.strip().lower().replace(' ', '_')
        self.pipelines = pipelines
        self.properties = properties
