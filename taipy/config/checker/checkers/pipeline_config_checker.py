from taipy.config._config import _Config
from taipy.config.checker.checkers.config_checker import ConfigChecker
from taipy.config.checker.issue_collector import IssueCollector
from taipy.config.pipeline_config import PipelineConfig
from taipy.config.task_config import TaskConfig


class PipelineConfigChecker(ConfigChecker):
    def __init__(self, config: _Config, collector: IssueCollector):
        super().__init__(config, collector)

    def check(self) -> IssueCollector:
        pipeline_configs = self.config.pipelines
        for pipeline_config_name, pipeline_config in pipeline_configs.items():
            if pipeline_config_name != "default":
                self._check_tasks(pipeline_config_name, pipeline_config)
        return self.collector

    def _check_tasks(self, pipeline_config_name: str, pipeline_config: PipelineConfig):
        self._check_children(
            PipelineConfig, pipeline_config_name, pipeline_config.TASK_KEY, pipeline_config.tasks, TaskConfig
        )
