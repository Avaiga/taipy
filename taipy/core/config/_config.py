from copy import copy
from typing import Dict

from taipy.core.config.data_node_config import DataNodeConfig
from taipy.core.config.global_app_config import GlobalAppConfig
from taipy.core.config.job_config import JobConfig

from .pipeline_config import PipelineConfig
from .scenario_config import ScenarioConfig
from .task_config import TaskConfig


class _Config:
    DEFAULT_KEY = "default"

    def __init__(self):
        self._global_config: GlobalAppConfig = GlobalAppConfig()
        self._job_config: JobConfig = JobConfig()
        self._data_nodes: Dict[str, DataNodeConfig] = {}
        self._tasks: Dict[str, TaskConfig] = {}
        self._pipelines: Dict[str, PipelineConfig] = {}
        self._scenarios: Dict[str, ScenarioConfig] = {}

    @classmethod
    def _default_config(cls):
        config = _Config()
        config._global_config = GlobalAppConfig.default_config()
        config._job_config = JobConfig().default_config()
        config._data_nodes = {cls.DEFAULT_KEY: DataNodeConfig.default_config(cls.DEFAULT_KEY)}
        config._tasks = {cls.DEFAULT_KEY: TaskConfig.default_config(cls.DEFAULT_KEY)}
        config._pipelines = {cls.DEFAULT_KEY: PipelineConfig.default_config(cls.DEFAULT_KEY)}
        config._scenarios = {cls.DEFAULT_KEY: ScenarioConfig.default_config(cls.DEFAULT_KEY)}
        return config

    def _update(self, other_config):
        self._global_config._update(other_config._global_config._to_dict())
        self._job_config._update(other_config._job_config._to_dict())
        self.__update_entity_configs(self._data_nodes, other_config._data_nodes, DataNodeConfig)
        self.__update_entity_configs(self._tasks, other_config._tasks, TaskConfig)
        self.__update_entity_configs(self._pipelines, other_config._pipelines, PipelineConfig)
        self.__update_entity_configs(self._scenarios, other_config._scenarios, ScenarioConfig)

    def __update_entity_configs(self, sub_configs, other_sub_configs, _class):
        if self.DEFAULT_KEY in other_sub_configs:
            if self.DEFAULT_KEY in sub_configs:
                sub_configs[self.DEFAULT_KEY]._update(other_sub_configs[self.DEFAULT_KEY]._to_dict())
            else:
                sub_configs[self.DEFAULT_KEY] = other_sub_configs[self.DEFAULT_KEY]
        for cfg_id, sub_config in other_sub_configs.items():
            if cfg_id != self.DEFAULT_KEY:
                if cfg_id in sub_configs:
                    sub_configs[cfg_id]._update(sub_config._to_dict(), sub_configs.get(self.DEFAULT_KEY))
                else:
                    sub_configs[cfg_id] = copy(sub_config)
                    sub_configs[cfg_id]._update(sub_config._to_dict(), sub_configs.get(self.DEFAULT_KEY))
