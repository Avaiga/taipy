import os
from typing import Any, Callable, Dict, List, Optional, Union

from taipy.core.common._classproperty import _Classproperty
from taipy.core.common._taipy_logger import _TaipyLogger
from taipy.core.common.frequency import Frequency
from taipy.core.common.scope import Scope
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
from taipy.core.exceptions.exceptions import ConfigurationIssueError


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
    def load(cls, filename):
        """
        Loads a toml file configuration located at the `filename` path given as parameter.

        Parameters:
            filename (str or Path): The path of the toml configuration file to load.
        """
        cls.__logger.info(f"Loading configuration. Filename: '{filename}'")
        cls._file_config = _TomlSerializer()._read(filename)
        cls.__compile_configs()
        cls.__logger.info(f"Configuration '{filename}' successfully loaded.")

    @classmethod
    def export(cls, filename):
        """
        Exports the configuration to a toml file.

        The configuration exported is a compilation from the three possible methods to configure the application:
        The python code configuration, the file configuration and the environment
        configuration.

        Parameters:
            filename (str or Path): The path of the file to export.
        Note:
            It overwrites the file if it already exists.
        """
        _TomlSerializer()._write(cls._applied_config, filename)

    @classmethod
    def _export_code_config(cls, filename):
        _TomlSerializer()._write(cls._python_config, filename)

    @classmethod
    def configure_global_app(
        cls,
        root_folder: str = None,
        storage_folder: str = None,
        clean_entities_enabled: Union[bool, str] = None,
        **properties,
    ) -> GlobalAppConfig:
        """
        Configures global application.

        Parameters:
            root_folder (Optional[str]): The path of the base folder for the taipy application.
            storage_folder (Optional[str]): The folder name used to store Taipy data.
                It is used in conjunction with the root_folder field. That means the storage path is
                "<root_folder><storage_folder>".
            clean_entities_enabled (Optional[str]): The field to activate/deactivate the clean entities feature.
                The default value is false.
        Returns:
            `GlobalAppConfig`: The global application configuration.
        """
        cls._python_config._global_config = GlobalAppConfig(
            root_folder, storage_folder, clean_entities_enabled, **properties
        )
        cls.__compile_configs()
        return cls._applied_config._global_config

    @classmethod
    def configure_job_executions(
        cls,
        mode: str = None,
        nb_of_workers: Union[int, str] = None,
        **properties,
    ) -> JobConfig:
        """
        Configures job execution.

        Parameters:
            mode (Optional[str]): The job execution mode.
                Possible values are: `standalone` (default value), or `airflow` (Enterprise version only).
            nb_of_workers (Optional[int, str]): The maximum number of jobs able to run in parallel. Default value: 1.
                A string can be provided as parameter to dynamically set the value using an environment variable.
                The string must follow the pattern: `ENV[<env_var>]` where `<env_var>` is an environment variable name.
        Returns:
            `JobConfig`: The job execution configuration.
        """
        job_config = JobConfig(
            mode,
            nb_of_workers,
            **properties,
        )
        cls._python_config._job_config = job_config
        cls.__compile_configs()
        return cls._applied_config._job_config

    @classmethod
    def configure_data_node(
        cls,
        id: str,
        storage_type: str = DataNodeConfig._DEFAULT_STORAGE_TYPE,
        scope: Scope = DataNodeConfig._DEFAULT_SCOPE,
        **properties,
    ) -> DataNodeConfig:
        """
        Configures a new data node configuration.

        Parameters:
            id (str): The unique identifier of the data node configuration.
            storage_type (str): The data node configuration storage type. The possible values are "pickle"
                (default value), "csv", "excel", "sql". "in_memory", "generic".
            scope (`Scope`): The scope of the data node configuration. The default value is Scope.SCENARIO.
            **properties (Dict[str, Any]): The variable length keyword arguments.
        Returns:
            `DataNodeConfig`: The new data node configuration.
        """
        dn_config = DataNodeConfig(id, storage_type, scope, **properties)
        cls._python_config._data_nodes[dn_config.id] = dn_config
        cls.__compile_configs()
        return cls._applied_config._data_nodes[dn_config.id]

    @classmethod
    def configure_default_data_node(
        cls, storage_type: str, scope=DataNodeConfig._DEFAULT_SCOPE, **properties
    ) -> DataNodeConfig:
        """
        Configures the default values of the data node configurations.

        Parameters:
            storage_type (str): The default storage type of the data node configurations. The possible values are "pickle"
                (default value), "csv", "excel", "sql". "in_memory", "generic".
            scope (`Scope`): The default scope of the data node configurations. The default value is Scope.SCENARIO.
            **properties (Dict[str, Any]): The variable length keyword arguments.
        Returns:
            `DataNodeConfig`: The default data node configuration.
        """
        data_node_config = DataNodeConfig(_Config.DEFAULT_KEY, storage_type, scope, **properties)
        cls._python_config._data_nodes[_Config.DEFAULT_KEY] = data_node_config
        cls.__compile_configs()
        return cls._applied_config._data_nodes[_Config.DEFAULT_KEY]

    @classmethod
    def configure_task(
        cls,
        id: str,
        function,
        input: Optional[Union[DataNodeConfig, List[DataNodeConfig]]] = None,
        output: Optional[Union[DataNodeConfig, List[DataNodeConfig]]] = None,
        **properties,
    ) -> TaskConfig:
        """
        Configures a new task configuration.

        Parameters:
            id (str): The unique identifier of the task configuration.
            function (Callable): The python function called by Taipy to run the task.
            input (Optional[Union[DataNodeConfig, List[DataNodeConfig]]]): The list of the function inputs as data node
                configurations.
            output (Optional[Union[DataNodeConfig, List[DataNodeConfig]]]): The list of the function outputs as data node
                configurations.
            **properties (Dict[str, Any]): The variable length keyword arguments.
        Returns:
            `TaskConfig`: The new task configuration.
        """
        task_config = TaskConfig(id, function, input, output, **properties)
        cls._python_config._tasks[task_config.id] = task_config
        cls.__compile_configs()
        return cls._applied_config._tasks[task_config.id]

    @classmethod
    def configure_default_task(
        cls,
        function,
        input: Optional[Union[DataNodeConfig, List[DataNodeConfig]]] = None,
        output: Optional[Union[DataNodeConfig, List[DataNodeConfig]]] = None,
        **properties,
    ) -> TaskConfig:
        """
        Configures the default values of the task configurations.

        Parameters:
            function (Callable): The python function called by Taipy to run the task.
            input (Optional[Union[DataNodeConfig, List[DataNodeConfig]]]): The list of the function inputs as data node
                configurations.
            output (Optional[Union[DataNodeConfig, List[DataNodeConfig]]]): The list of the function outputs as data node
                configurations.
            **properties (Dict[str, Any]): The variable length keyword arguments.
        Returns:
            `TaskConfig`: The default task configuration.
        """
        task_config = TaskConfig(_Config.DEFAULT_KEY, function, input, output, **properties)
        cls._python_config._tasks[task_config.id] = task_config
        cls.__compile_configs()
        return cls._applied_config._tasks[_Config.DEFAULT_KEY]

    @classmethod
    def configure_pipeline(
        cls, id: str, task_configs: Union[TaskConfig, List[TaskConfig]], **properties
    ) -> PipelineConfig:
        """
        Configures a new pipeline configuration.

        Parameters:
            id (str): The unique identifier of the pipeline configuration.
            task_configs (Callable): The list of the task configurations.
            **properties (Dict[str, Any]): The variable length keyword arguments.
        Returns:
            `PipelineConfig`: The new pipeline configuration.
        """
        pipeline_config = PipelineConfig(id, task_configs, **properties)
        cls._python_config._pipelines[pipeline_config.id] = pipeline_config
        cls.__compile_configs()
        return cls._applied_config._pipelines[pipeline_config.id]

    @classmethod
    def configure_default_pipeline(
        cls, task_configs: Union[TaskConfig, List[TaskConfig]], **properties
    ) -> PipelineConfig:
        """
        Configures the default values of the pipeline configurations.

        Parameters:
            task_configs (Callable): The list of the task configurations.
            **properties (Dict[str, Any]): The variable length keyword arguments.
        Returns:
            `PipelineConfig`: The default pipeline configuration.
        """
        pipeline_config = PipelineConfig(_Config.DEFAULT_KEY, task_configs, **properties)
        cls._python_config._pipelines[_Config.DEFAULT_KEY] = pipeline_config
        cls.__compile_configs()
        return cls._applied_config._pipelines[_Config.DEFAULT_KEY]

    @classmethod
    def configure_scenario(
        cls,
        id: str,
        pipeline_configs: List[PipelineConfig],
        frequency: Optional[Frequency] = None,
        comparators: Optional[Dict[str, Union[List[Callable], Callable]]] = None,
        **properties,
    ) -> ScenarioConfig:
        """
        Configures a new scenario configuration.

        Parameters:
            id (str): The unique identifier of the scenario configuration.
            pipeline_configs (Callable): The list of the pipeline configurations.
            frequency (Optional[`Frequency`]): The scenario frequency.
                It corresponds to the recurrence of the scenarios instantiated from this configuration. Based on this
                frequency each scenario will be attached to the right cycle.
            comparators (Optional[Dict[str, Union[List[Callable], Callable]]]): The list of functions used to compare
                scenarios. A comparator function is attached to a scenario's data node configuration. The key of
                the dictionary parameter corresponds to the data node configuration id. During the scenarios' comparison,
                each comparator is applied to all the data nodes instantiated from the data node configuration attached
                to the comparator.
            **properties (Dict[str, Any]): The variable length keyword arguments.
        Returns:
            `ScenarioConfig`: The new scenario configuration.
        """
        scenario_config = ScenarioConfig(
            id, pipeline_configs, frequency=frequency, comparators=comparators, **properties
        )
        cls._python_config._scenarios[scenario_config.id] = scenario_config
        cls.__compile_configs()
        return cls._applied_config._scenarios[scenario_config.id]

    @classmethod
    def configure_scenario_from_tasks(
        cls,
        id: str,
        task_configs: List[TaskConfig],
        frequency: Optional[Frequency] = None,
        comparators: Optional[Dict[str, Union[List[Callable], Callable]]] = None,
        pipeline_id: Optional[str] = None,
        **properties,
    ) -> ScenarioConfig:
        """
        Configures a new scenario configuration made of a single new pipeline configuration. A new pipeline configuration is
        created as well. If no pipeline_id is provided, it will be the scenario configuration id post-fixed by '_pipeline'.

        Parameters:
            id (str): The unique identifier of the scenario configuration.
            task_configs (Callable): The list of the task configurations.
            frequency (Optional[`Frequency`]): The scenario frequency.
                It corresponds to the recurrence of the scenarios instantiated from this configuration. Based on this
                frequency each scenario will be attached to the right cycle.
            comparators (Optional[Dict[str, Union[List[Callable], Callable]]]): The list of functions used to compare
                scenarios. A comparator function is attached to a scenario's data node configuration. The key of
                the dictionary parameter corresponds to the data node configuration id. During the scenarios' comparison,
                each comparator is applied to all the data nodes instantiated from the data node configuration attached
                to the comparator.
            pipeline_id (str): The id of the pipeline configuration to be configured.
            **properties (Dict[str, Any]): The variable length keyword arguments.
        Returns:
            `ScenarioConfig`: The new scenario configuration.
        """
        if not pipeline_id:
            pipeline_id = f"{id}_pipeline"
        pipeline_config = cls.configure_pipeline(pipeline_id, task_configs, **properties)
        return cls.configure_scenario(id, [pipeline_config], frequency=frequency, comparators=comparators, **properties)

    @classmethod
    def configure_default_scenario(
        cls,
        pipeline_configs: List[PipelineConfig],
        frequency: Optional[Frequency] = None,
        comparators: Optional[Dict[str, Union[List[Callable], Callable]]] = None,
        **properties,
    ):
        """
        Configures the default values of the scenario configurations.

        Parameters:
            pipeline_configs (Callable): The list of the pipeline configurations.
            frequency (Optional[`Frequency`]): The scenario frequency.
                It corresponds to the recurrence of the scenarios instantiated from this configuration. Based on this
                frequency each scenario will be attached to the right cycle.
            comparators (Optional[Dict[str, Union[List[Callable], Callable]]]): The list of functions used to compare
                scenarios. A comparator function is attached to a scenario's data node configuration. The key of
                the dictionary parameter corresponds to the data node configuration id. During the scenarios' comparison,
                each comparator is applied to all the data nodes instantiated from the data node configuration attached
                to the comparator.
            **properties (Dict[str, Any]): The variable length keyword arguments.
        Returns:
            `ScenarioConfig`: The default scenario configuration.
        """
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
    def check(cls) -> IssueCollector:
        """
        Checks configuration, logs issue messages and returns an issue collector.

        Returns:
            `IssueCollector`: Collector containing the info, the warning and the error issues.
        """
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

    @classmethod
    def configure_csv_data_node(
        cls, id: str, path: str, has_header=True, scope=DataNodeConfig._DEFAULT_SCOPE, **properties
    ):
        """
        Configures a new CSV data node configuration.

        Parameters:
            id (str): The unique identifier of the data node configuration.
            path (str): The path of the CSV file.
            has_header (bool): The parameter to define if the CSV file has a header or not.
            scope (`Scope`): The scope of the CSV data node configuration. The default value is Scope.SCENARIO.
            **properties (Dict[str, Any]): The variable length keyword arguments.
        Returns:
            `DataNodeConfig`: The new CSV data node configuration.
        """
        from taipy.core.data import CSVDataNode

        return cls.configure_data_node(
            id, CSVDataNode.storage_type(), scope=scope, path=path, has_header=has_header, **properties
        )

    @classmethod
    def configure_excel_data_node(
        cls,
        id: str,
        path: str,
        has_header: bool = True,
        sheet_name: Union[List[str], str] = "Sheet1",
        scope: Scope = DataNodeConfig._DEFAULT_SCOPE,
        **properties,
    ):
        """
        Configures a new Excel data node configuration.

        Parameters:
            id (str): The unique identifier of the data node configuration.
            path (str): The path of the Excel file.
            has_header (bool): The parameter to define if the Excel file has a header or not.
            sheet_name (str): The sheet names.
            scope (`Scope`): The scope of the Excel data node configuration. The default value is Scope.SCENARIO.
            **properties (Dict[str, Any]): The variable length keyword arguments.
        Returns:
            `DataNodeConfig`: The new CSV data node configuration.
        """
        from taipy.core.data import ExcelDataNode

        return cls.configure_data_node(
            id,
            ExcelDataNode.storage_type(),
            scope=scope,
            path=path,
            has_header=has_header,
            sheet_name=sheet_name,
            **properties,
        )

    @classmethod
    def configure_generic_data_node(
        cls,
        id: str,
        read_fct: Callable = None,
        write_fct: Callable = None,
        read_fct_params: List = None,
        write_fct_params: List = None,
        scope: Scope = DataNodeConfig._DEFAULT_SCOPE,
        **properties,
    ):
        """
        Configures a new Generic data node configuration.

        Parameters:
            id (str): The unique identifier of the data node configuration.
            read_fct (Callable): The python function called by Taipy to read the data.
            write_fct (Callable): The python function called by Taipy to write the data. The provided function must have at least
                1 parameter to receive the date to be written.
            read_fct_params (List): The parameters that will be passed to read_fct to read the data.
            write_fct_params (List): The parameters that will be passed to write_fct to write the data.
            scope (`Scope`): The scope of the Generic data node configuration. The default value is Scope.SCENARIO.
            **properties (Dict[str, Any]): The variable length keyword arguments.
        Returns:
            `DataNodeConfig`: The new Generic data node configuration.
        """
        from taipy.core.data import GenericDataNode

        return cls.configure_data_node(
            id,
            GenericDataNode.storage_type(),
            scope=scope,
            read_fct=read_fct,
            write_fct=write_fct,
            read_fct_params=read_fct_params,
            write_fct_params=write_fct_params,
            **properties,
        )

    @classmethod
    def configure_in_memory_data_node(
        cls, id: str, default_data: Optional[Any] = None, scope: Scope = DataNodeConfig._DEFAULT_SCOPE, **properties
    ):
        """
        Configures a new in_memory data node configuration.

        Parameters:
            id (str): The unique identifier of the data node configuration.
            default_data (Optional[Any]): The default data of the data nodes instantiated from the in_memory data node
                configuration.
            scope (`Scope`): The scope of the in_memory data node configuration. The default value is Scope.SCENARIO.
            **properties (Dict[str, Any]): The variable length keyword arguments.
        Returns:
            `DataNodeConfig`: The new in_memory data node configuration.
        """
        from taipy.core.data import InMemoryDataNode

        return cls.configure_data_node(
            id, InMemoryDataNode.storage_type(), scope=scope, default_data=default_data, **properties
        )

    @classmethod
    def configure_pickle_data_node(
        cls, id: str, default_data: Optional[Any] = None, scope: Scope = DataNodeConfig._DEFAULT_SCOPE, **properties
    ):
        """
        Configures a new pickle data node configuration.

        Parameters:
            id (str): The unique identifier of the data node configuration.
            default_data (Optional[Any]): The default data of the data nodes instantiated from the pickle data node
                configuration.
            scope (`Scope`): The scope of the pickle data node configuration. The default value is Scope.SCENARIO.
            **properties (Dict[str, Any]): The variable length keyword arguments.
        Returns:
            `DataNodeConfig`: The new pickle data node configuration.
        """
        from taipy.core.data import PickleDataNode

        return cls.configure_data_node(
            id, PickleDataNode.storage_type(), scope=scope, default_data=default_data, **properties
        )

    @classmethod
    def configure_sql_data_node(
        cls,
        id: str,
        db_username: str,
        db_password: str,
        db_name: str,
        db_engine: str,
        read_query: str,
        write_table: str = None,
        db_port: int = 1433,
        db_host: str = "localhost",
        db_driver: str = "ODBC Driver 17 for SQL Server",
        scope: Scope = DataNodeConfig._DEFAULT_SCOPE,
        **properties,
    ):
        """
        Configures a new SQL data node configuration.

        Parameters:
            id (str): The unique identifier of the data node configuration.
            db_username (str): The database username.
            db_password (str): The database password.
            db_name (str): The database name.
            db_engine (str): The database engine. Possible values are 'sqlite' or 'mssql'.
            read_query (str): The SQL query called by Taipy to read the data from the database.
            write_table (str): The name of the table in the database to write the data to.
            db_port (int): The database port. The default value is 1433.
            db_host (str): The database host. The default value is 'localhost'.
            db_driver (str): The database driver. The default value is 'ODBC Driver 17 for SQL Server'.
            scope (`Scope`): The scope of the SQL data node configuration. The default value is Scope.SCENARIO.
            **properties (Dict[str, Any]): The variable length keyword arguments.
        Returns:
            `DataNodeConfig`: The new SQL data node configuration.
        """
        from taipy.core.data import SQLDataNode

        return cls.configure_data_node(
            id,
            SQLDataNode.storage_type(),
            scope=scope,
            db_username=db_username,
            db_password=db_password,
            db_name=db_name,
            db_host=db_host,
            db_engine=db_engine,
            db_driver=db_driver,
            read_query=read_query,
            write_table=write_table,
            db_port=db_port,
            **properties,
        )


Config._load_environment_file_config()
