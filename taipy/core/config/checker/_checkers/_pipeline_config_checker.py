from taipy.core.config._config import _Config
from taipy.core.config.checker._checkers._config_checker import _ConfigChecker
from taipy.core.config.checker.issue_collector import IssueCollector
from taipy.core.config.pipeline_config import PipelineConfig
from taipy.core.config.task_config import TaskConfig


class _PipelineConfigChecker(_ConfigChecker):
    def __init__(self, config: _Config, collector: IssueCollector):
        super().__init__(config, collector)

    def _check(self) -> IssueCollector:
        pipeline_configs = self._config._pipelines
        for pipeline_config_id, pipeline_config in pipeline_configs.items():
            if pipeline_config_id != _Config.DEFAULT_KEY:
                self._check_existing_config_id(pipeline_config)
                self._check_tasks(pipeline_config_id, pipeline_config)
        return self._collector

    def _check_tasks(self, pipeline_config_id: str, pipeline_config: PipelineConfig):
        self._check_children(
            PipelineConfig, pipeline_config_id, pipeline_config._TASK_KEY, pipeline_config.tasks, TaskConfig
        )
