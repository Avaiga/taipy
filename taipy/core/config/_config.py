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
        self.global_config: GlobalAppConfig = GlobalAppConfig()
        self.job_config: JobConfig = JobConfig()
        self.data_nodes: Dict[str, DataNodeConfig] = {}
        self.tasks: Dict[str, TaskConfig] = {}
        self.pipelines: Dict[str, PipelineConfig] = {}
        self.scenarios: Dict[str, ScenarioConfig] = {}

    @classmethod
    def default_config(cls):
        config = _Config()
        config.global_config = GlobalAppConfig.default_config()
        config.job_config = JobConfig().default_config()
        config.data_nodes = {cls.DEFAULT_KEY: DataNodeConfig.default_config(cls.DEFAULT_KEY)}
        config.tasks = {cls.DEFAULT_KEY: TaskConfig.default_config(cls.DEFAULT_KEY)}
        config.pipelines = {cls.DEFAULT_KEY: PipelineConfig.default_config(cls.DEFAULT_KEY)}
        config.scenarios = {cls.DEFAULT_KEY: ScenarioConfig.default_config(cls.DEFAULT_KEY)}
        return config

    def update(self, other_config):
        self.global_config.update(other_config.global_config.to_dict())
        self.job_config.update(other_config.job_config.to_dict())
        self.__update_entity_configs(self.data_nodes, other_config.data_nodes, DataNodeConfig)
        self.__update_entity_configs(self.tasks, other_config.tasks, TaskConfig)
        self.__update_entity_configs(self.pipelines, other_config.pipelines, PipelineConfig)
        self.__update_entity_configs(self.scenarios, other_config.scenarios, ScenarioConfig)

    def __update_entity_configs(self, sub_configs, other_sub_configs, _class):
        if self.DEFAULT_KEY in other_sub_configs:
            if self.DEFAULT_KEY in sub_configs:
                sub_configs[self.DEFAULT_KEY].update(other_sub_configs[self.DEFAULT_KEY].to_dict())
            else:
                sub_configs[self.DEFAULT_KEY] = other_sub_configs[self.DEFAULT_KEY]
        for name, dn_config in other_sub_configs.items():
            if name != self.DEFAULT_KEY:
                if name in sub_configs:
                    sub_configs[name].update(dn_config.to_dict(), sub_configs.get(self.DEFAULT_KEY))
                else:
                    sub_configs[name] = copy(dn_config)
                    sub_configs[name].update(dn_config.to_dict(), sub_configs.get(self.DEFAULT_KEY))
