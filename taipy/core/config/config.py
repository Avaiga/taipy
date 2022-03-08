__all__ = ["Config"]

import os
from typing import Callable, Dict, List, Optional, Union

from taipy.core.common._classproperty import _Classproperty
from taipy.core.common._taipy_logger import _TaipyLogger
from taipy.core.common.frequency import Frequency
from taipy.core.config._config import _Config
from taipy.core.config._toml_serializer import _TomlSerializer
from taipy.core.config.checker._checker import _Checker
from taipy.core.config.checker.issue_collector import IssueCollector
from taipy.core.config.data_node_config import DataNodeConfig
from taipy.core.config.global_app_config import GlobalAppConfig
from taipy.core.config.job_config import JobConfig
from taipy.core.config.pipeline_config import PipelineConfig
from taipy.core.config.scenario_config import ScenarioConfig
from taipy.core.config.task_config import TaskConfig
from taipy.core.data.scope import Scope
from taipy.core.exceptions.configuration import ConfigurationIssueError


class Config:
    """Configuration singleton."""

    _ENVIRONMENT_VARIABLE_NAME_WITH_CONFIG_PATH = "TAIPY_CONFIG_PATH"
    __logger = _TaipyLogger._get_logger()
    _python_config = _Config()
    _file_config = None
    _env_file_config = None
    _applied_config = _Config._default_config()
    _collector = IssueCollector()

    @_Classproperty
    def job_config(cls) -> JobConfig:
        """Returns configuration values related to the job executions as a `JobConfig^`."""
        return cls._applied_config._job_config

    @_Classproperty
    def global_config(cls) -> GlobalAppConfig:
        """Returns configuration values related to the global application as a `GlobalAppConfig^`."""
        return cls._applied_config._global_config

    @_Classproperty
    def data_nodes(cls) -> Dict[str, DataNodeConfig]:
        """Returns data node configs by config id."""
        return cls._applied_config._data_nodes

    @_Classproperty
    def tasks(cls) -> Dict[str, TaskConfig]:
        """Returns task configs by config id."""
        return cls._applied_config._tasks

    @_Classproperty
    def pipelines(cls) -> Dict[str, PipelineConfig]:
        """Returns pipeline configs by config id."""
        return cls._applied_config._pipelines

    @_Classproperty
    def scenarios(cls) -> Dict[str, ScenarioConfig]:
        """Returns scenario configs by config id."""
        return cls._applied_config._scenarios

    @classmethod
    def _load(cls, filename):

        cls._file_config = _TomlSerializer()._read(filename)
        cls.__compile_configs()

    @classmethod
    def _export(cls, filename):
        _TomlSerializer()._write(cls._applied_config, filename)

    @classmethod
    def _export_code_config(cls, filename):
        """
        Exports the python code configuration as a toml file.

        Parameters:
            filename (str): File to export.
        Note:
            Overwrite the file if it already exists.
        """
        _TomlSerializer()._write(cls._python_config, filename)

    @classmethod
    def _set_global_config(
        cls,
        root_folder: str = None,
        storage_folder: str = None,
        clean_entities_enabled: Union[bool, str] = None,
        **properties,
    ) -> GlobalAppConfig:
        cls._python_config._global_config = GlobalAppConfig(
            root_folder, storage_folder, clean_entities_enabled, **properties
        )
        cls.__compile_configs()
        return cls._applied_config._global_config

    @classmethod
    def _set_job_config(
        cls,
        mode: str = None,
        nb_of_workers: Union[int, str] = None,
        **properties,
    ):
        job_config = JobConfig(
            mode,
            nb_of_workers,
            **properties,
        )
        cls._python_config._job_config = job_config
        cls.__compile_configs()
        return cls._applied_config._job_config

    @classmethod
    def _add_data_node(
        cls,
        id: str,
        storage_type: str = DataNodeConfig._DEFAULT_STORAGE_TYPE,
        scope: Scope = DataNodeConfig._DEFAULT_SCOPE,
        **properties,
    ):
        dn_config = DataNodeConfig(id, storage_type, scope, **properties)
        cls._python_config._data_nodes[dn_config.id] = dn_config
        cls.__compile_configs()
        return cls._applied_config._data_nodes[dn_config.id]

    @classmethod
    def _add_default_data_node(cls, storage_type: str, scope=DataNodeConfig._DEFAULT_SCOPE, **properties):
        data_node_config = DataNodeConfig(_Config.DEFAULT_KEY, storage_type, scope, **properties)
        cls._python_config._data_nodes[_Config.DEFAULT_KEY] = data_node_config
        cls.__compile_configs()
        return cls._applied_config._data_nodes[_Config.DEFAULT_KEY]

    @classmethod
    def _add_task(
        cls,
        id: str,
        function,
        input: Optional[Union[DataNodeConfig, List[DataNodeConfig]]] = None,
        output: Optional[Union[DataNodeConfig, List[DataNodeConfig]]] = None,
        **properties,
    ):
        task_config = TaskConfig(id, function, input, output, **properties)
        cls._python_config._tasks[task_config.id] = task_config
        cls.__compile_configs()
        return cls._applied_config._tasks[task_config.id]

    @classmethod
    def _add_default_task(
        cls,
        function,
        input: Optional[Union[DataNodeConfig, List[DataNodeConfig]]] = None,
        output: Optional[Union[DataNodeConfig, List[DataNodeConfig]]] = None,
        **properties,
    ):
        task_config = TaskConfig(_Config.DEFAULT_KEY, function, input, output, **properties)
        cls._python_config._tasks[task_config.id] = task_config
        cls.__compile_configs()
        return cls._applied_config._tasks[_Config.DEFAULT_KEY]

    @classmethod
    def _add_pipeline(cls, id: str, task_configs: Union[TaskConfig, List[TaskConfig]], **properties):
        pipeline_config = PipelineConfig(id, task_configs, **properties)
        cls._python_config._pipelines[pipeline_config.id] = pipeline_config
        cls.__compile_configs()
        return cls._applied_config._pipelines[pipeline_config.id]

    @classmethod
    def _add_default_pipeline(cls, task_configs: Union[TaskConfig, List[TaskConfig]], **properties):
        pipeline_config = PipelineConfig(_Config.DEFAULT_KEY, task_configs, **properties)
        cls._python_config._pipelines[_Config.DEFAULT_KEY] = pipeline_config
        cls.__compile_configs()
        return cls._applied_config._pipelines[_Config.DEFAULT_KEY]

    @classmethod
    def _add_scenario(
        cls,
        id: str,
        pipeline_configs: List[PipelineConfig],
        frequency: Optional[Frequency] = None,
        comparators: Optional[Dict[str, Union[List[Callable], Callable]]] = None,
        **properties,
    ):
        scenario_config = ScenarioConfig(
            id, pipeline_configs, frequency=frequency, comparators=comparators, **properties
        )
        cls._python_config._scenarios[scenario_config.id] = scenario_config
        cls.__compile_configs()
        return cls._applied_config._scenarios[scenario_config.id]

    @classmethod
    def _add_scenario_from_tasks(
        cls,
        id: str,
        task_configs: List[TaskConfig],
        frequency: Optional[Frequency] = None,
        comparators: Optional[Dict[str, Union[List[Callable], Callable]]] = None,
        pipeline_id: Optional[str] = None,
        **properties,
    ):
        if not pipeline_id:
            pipeline_id = f"{id}_pipeline"
        pipeline_config = cls._add_pipeline(pipeline_id, task_configs, **properties)
        return cls._add_scenario(id, [pipeline_config], frequency=frequency, comparators=comparators, **properties)

    @classmethod
    def _add_default_scenario(
        cls,
        pipeline_configs: List[PipelineConfig],
        frequency: Optional[Frequency] = None,
        comparators: Optional[Dict[str, Union[List[Callable], Callable]]] = None,
        **properties,
    ):
        scenario_config = ScenarioConfig(
            _Config.DEFAULT_KEY, pipeline_configs, frequency=frequency, comparators=comparators, **properties
        )
        cls._python_config._scenarios[_Config.DEFAULT_KEY] = scenario_config
        cls.__compile_configs()
        return cls._applied_config._scenarios[_Config.DEFAULT_KEY]

    @classmethod
    def _load_environment_file_config(cls):
        if config_filename := os.environ.get(cls._ENVIRONMENT_VARIABLE_NAME_WITH_CONFIG_PATH):
            cls.__logger.info(f"Loading configuration provided by environment variable. Filename: '{config_filename}'")
            cls._env_file_config = _TomlSerializer()._read(config_filename)
            cls.__logger.info(f"Configuration '{config_filename}' successfully loaded.")

    @classmethod
    def __compile_configs(cls):
        Config._load_environment_file_config()
        cls._applied_config = _Config._default_config()
        if cls._python_config:
            cls._applied_config._update(cls._python_config)
        if cls._file_config:
            cls._applied_config._update(cls._file_config)
        if cls._env_file_config:
            cls._applied_config._update(cls._env_file_config)

    @classmethod
    def _check(cls) -> IssueCollector:
        cls._collector = _Checker()._check(cls._applied_config)
        cls.__log_message(cls)
        return cls._collector

    @classmethod
    def __log_message(cls, config):
        for issue in config._collector._warnings:
            cls.__logger.warning(str(issue))
        for issue in config._collector._infos:
            cls.__logger.info(str(issue))
        for issue in config._collector._errors:
            cls.__logger.error(str(issue))
        if len(config._collector._errors) != 0:
            raise ConfigurationIssueError


Config._load_environment_file_config()
