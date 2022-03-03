from taipy.core.config._config import _Config
from taipy.core.config.checker.checkers.config_checker import ConfigChecker
from taipy.core.config.checker.issue_collector import IssueCollector
from taipy.core.config.data_node_config import DataNodeConfig
from taipy.core.config.task_config import TaskConfig


class TaskConfigChecker(ConfigChecker):
    def __init__(self, config: _Config, collector: IssueCollector):
        super().__init__(config, collector)

    def check(self) -> IssueCollector:
        task_configs = self.config.tasks
        for task_config_id, task_config in task_configs.items():
            if task_config_id != _Config.DEFAULT_KEY:
                self._check_existing_config_id(task_config)
                self._check_existing_function(task_config_id, task_config)
                self._check_inputs(task_config_id, task_config)
                self._check_outputs(task_config_id, task_config)
        return self.collector

    def _check_inputs(self, task_config_id: str, task_config: TaskConfig):
        self._check_children(TaskConfig, task_config_id, task_config.INPUT_KEY, task_config.inputs, DataNodeConfig)

    def _check_outputs(self, task_config_id: str, task_config: TaskConfig):
        self._check_children(TaskConfig, task_config_id, task_config.OUTPUT_KEY, task_config.outputs, DataNodeConfig)

    def _check_existing_function(self, task_config_id: str, task_config: TaskConfig):
        if not task_config.function:
            self._error(
                task_config.FUNCTION,
                task_config.function,
                f"{task_config.FUNCTION} field of Task {task_config_id} is empty.",
            )
        else:
            if not callable(task_config.function):
                self._error(
                    task_config.FUNCTION,
                    task_config.function,
                    f"{task_config.FUNCTION} field of task {task_config_id} must be populated with Callable value.",
                )
