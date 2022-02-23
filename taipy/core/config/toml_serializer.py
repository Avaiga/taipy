from typing import Any, Dict, Optional

import toml  # type: ignore

from taipy.core.common.frequency import Frequency
from taipy.core.common.unicode_to_python_variable_name import protect_name
from taipy.core.config._config import _Config
from taipy.core.config.data_node_config import DataNodeConfig
from taipy.core.config.global_app_config import GlobalAppConfig
from taipy.core.config.job_config import JobConfig
from taipy.core.config.pipeline_config import PipelineConfig
from taipy.core.config.scenario_config import ScenarioConfig
from taipy.core.config.task_config import TaskConfig
from taipy.core.data.scope import Scope
from taipy.core.exceptions.configuration import LoadingError


class TomlSerializer:
    """Convert configuration from TOML representation to Python Dict and reciprocally."""

    GLOBAL_NODE_NAME = "TAIPY"
    JOB_NODE_NAME = "JOB"
    DATA_NODE_NAME = "DATA_NODE"
    TASK_NODE_NAME = "TASK"
    PIPELINE_NODE_NAME = "PIPELINE"
    SCENARIO_NODE_NAME = "SCENARIO"

    @classmethod
    def write(cls, configuration: _Config, filename: str):
        config = {
            cls.GLOBAL_NODE_NAME: configuration.global_config.to_dict(),
            cls.JOB_NODE_NAME: configuration.job_config.to_dict(),
            cls.DATA_NODE_NAME: cls.__to_dict(configuration.data_nodes),
            cls.TASK_NODE_NAME: cls.__to_dict(configuration.tasks),
            cls.PIPELINE_NODE_NAME: cls.__to_dict(configuration.pipelines),
            cls.SCENARIO_NODE_NAME: cls.__to_dict(configuration.scenarios),
        }
        with open(filename, "w") as fd:
            toml.dump(cls.__stringify(config), fd)

    @classmethod
    def __to_dict(cls, dict_of_configs: Dict[str, Any]):
        return {key: value.to_dict() for key, value in dict_of_configs.items()}

    @classmethod
    def __stringify(cls, config):
        if config is None:
            return None
        if isinstance(config, Scope):
            return config.name
        if isinstance(config, Frequency):
            return config.name
        if isinstance(config, DataNodeConfig):
            return config.name
        if isinstance(config, TaskConfig):
            return config.name
        if isinstance(config, PipelineConfig):
            return config.name
        if isinstance(config, dict):
            return {str(key): cls.__stringify(val) for key, val in config.items()}
        if isinstance(config, list):
            return [cls.__stringify(val) for val in config]
        return config

    @classmethod
    def read(cls, filename: str) -> _Config:
        try:
            return cls.__from_dict(dict(toml.load(filename)))
        except toml.TomlDecodeError as e:
            error_msg = f"Can not load configuration {e}"
            raise LoadingError(error_msg)

    @staticmethod
    def extract_node(config_as_dict, cls_config, node, config: Optional[dict]):
        res = {}
        for key, value in config_as_dict.get(node, {}).items():
            key = protect_name(key)
            res[key] = cls_config.from_dict(key, value) if config is None else cls_config.from_dict(key, value, config)
        return res

    @classmethod
    def __from_dict(cls, config_as_dict) -> _Config:
        config = _Config()
        config.global_config = GlobalAppConfig.from_dict(config_as_dict.get(cls.GLOBAL_NODE_NAME, {}))
        config.job_config = JobConfig.from_dict(config_as_dict.get(cls.JOB_NODE_NAME, {}))
        config.data_nodes = cls.extract_node(config_as_dict, DataNodeConfig, cls.DATA_NODE_NAME, None)
        config.tasks = cls.extract_node(config_as_dict, TaskConfig, cls.TASK_NODE_NAME, config.data_nodes)
        config.pipelines = cls.extract_node(config_as_dict, PipelineConfig, cls.PIPELINE_NODE_NAME, config.tasks)
        config.scenarios = cls.extract_node(config_as_dict, ScenarioConfig, cls.SCENARIO_NODE_NAME, config.pipelines)
        return config
