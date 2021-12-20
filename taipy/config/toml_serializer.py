import logging
from typing import Any, Dict

import toml  # type: ignore

from taipy.config import DataSourceConfig, GlobalAppConfig, JobConfig, ScenarioConfig
from taipy.config._config import _Config
from taipy.config.pipeline_config import PipelineConfig
from taipy.config.task_config import TaskConfig
from taipy.cycle.frequency import Frequency
from taipy.data import Scope
from taipy.exceptions.configuration import LoadingError


class TomlSerializer:
    """Convert configuration from TOML representation to Python Dict and reciprocally."""

    GLOBAL_NODE_NAME = "TAIPY"
    JOB_NODE_NAME = "JOB"
    DATA_SOURCE_NODE_NAME = "DATA_SOURCE"
    TASK_NODE_NAME = "TASK"
    PIPELINE_NODE_NAME = "PIPELINE"
    SCENARIO_NODE_NAME = "SCENARIO"

    @classmethod
    def write(cls, configuration: _Config, filename: str):
        config = {
            cls.GLOBAL_NODE_NAME: configuration.global_config.to_dict(),
            cls.JOB_NODE_NAME: configuration.job_config.to_dict(),
            cls.DATA_SOURCE_NODE_NAME: cls.__to_dict(configuration.data_sources),
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
        if isinstance(config, DataSourceConfig):
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
            logging.error(error_msg)
            raise LoadingError(error_msg)

    @classmethod
    def __from_dict(cls, config_as_dict) -> _Config:
        config = _Config()
        config.global_config = GlobalAppConfig.from_dict(config_as_dict.get(cls.GLOBAL_NODE_NAME, {}))
        config.job_config = JobConfig.from_dict(config_as_dict.get(cls.JOB_NODE_NAME, {}))
        config.data_sources = {
            key: DataSourceConfig.from_dict(key, value)
            for key, value in config_as_dict.get(cls.DATA_SOURCE_NODE_NAME, {}).items()
        }
        config.tasks = {
            key: TaskConfig.from_dict(key, value, config.data_sources)
            for key, value in config_as_dict.get(cls.TASK_NODE_NAME, {}).items()
        }
        config.pipelines = {
            key: PipelineConfig.from_dict(key, value, config.tasks)
            for key, value in config_as_dict.get(cls.PIPELINE_NODE_NAME, {}).items()
        }
        config.scenarios = {
            key: ScenarioConfig.from_dict(key, value, config.pipelines)
            for key, value in config_as_dict.get(cls.SCENARIO_NODE_NAME, {}).items()
        }
        return config
