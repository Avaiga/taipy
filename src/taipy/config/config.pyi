# Copyright 2023 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import json
from typing import Any, Callable, Dict, List, Union, Optional

from .checker.issue_collector import IssueCollector
from .common._classproperty import _Classproperty
from .common._config_blocker import _ConfigBlocker
from .common.scope import Scope
from .common.frequency import Frequency
from .global_app.global_app_config import GlobalAppConfig
from .section import Section
from .unique_section import UniqueSection

from taipy.core.config import (
    DataNodeConfig,
    JobConfig,
    TaskConfig,
    PipelineConfig,
    ScenarioConfig,
)

class Config:
    @_Classproperty
    def unique_sections(cls) -> Dict[str, UniqueSection]:
        """Return all unique sections."""
    @_Classproperty
    def sections(cls) -> Dict[str, Dict[str, Section]]:
        """Return all non unique sections."""
    @_Classproperty
    def global_config(cls) -> GlobalAppConfig:
        """Return configuration values related to the global application as a `GlobalAppConfig^`."""
    @classmethod
    @_ConfigBlocker._check()
    def load(cls, filename):
        """Load a configuration file to replace the current python config and trigger the Config compilation.
        Parameters:
            filename (Union[str, Path]): The path of the toml configuration file to load.
        """
    @classmethod
    def export(cls, filename):
        """Export a configuration.

        The export is done in a toml file.

        The exported configuration is taken from the python code configuration.

        Parameters:
            filename (Union[str, Path]): The path of the file to export.
        Note:
            If _filename_ already exists, it is overwritten.
        """
    @classmethod
    def backup(cls, filename):
        """Backup a configuration.

        The backup is done in a toml file.

        The backed up configuration is a compilation from the three possible methods to configure
        the application: the python code configuration, the file configuration and the environment
        configuration.

        Parameters:
            filename (Union[str, Path]): The path of the file to export.
        Note:
            If _filename_ already exists, it is overwritten.
        """
    @classmethod
    @_ConfigBlocker._check()
    def restore(cls, filename):
        """Restore a configuration file and replace the current applied configuration.

        Parameters:
            filename (Union[str, Path]): The path of the toml configuration file to load.
        """
    @classmethod
    @_ConfigBlocker._check()
    def override(cls, filename):
        """Load a configuration from a file and overrides the current config.

        Parameters:
            filename (Union[str, Path]): The path of the toml configuration file to load.
        """
    @classmethod
    def block_update(cls):
        """Block update on the configuration signgleton."""
    @classmethod
    def unblock_update(cls):
        """Unblock update on the configuration signgleton."""
    @classmethod
    @_ConfigBlocker._check()
    def _register_default(cls, default_section: Section):
        """"""
    @classmethod
    @_ConfigBlocker._check()
    def _register(cls, section):
        """"""
    @classmethod
    def configure_global_app(
        cls,
        root_folder: str = ...,
        storage_folder: str = ...,
        clean_entities_enabled: Union[bool, str] = ...,
        **properties: Dict[str, Any],
    ) -> GlobalAppConfig:
        """Configure the global application.
        Parameters:
            root_folder (Optional[str]): The path of the base folder for the Taipy application.
            storage_folder (Optional[str]): The folder name used to store Taipy data.
                It is used in conjunction with the root_folder field: the storage path is
                "<root_folder><storage_folder>".
            clean_entities_enabled (Optional[str]): The field to activate or deactivate the
                'clean entities' feature. The default value is False.
        Returns:
            The global application configuration.
        """

    @classmethod
    def check(cls) -> IssueCollector:
        """Check configuration.

        This method logs issue messages and returns an issue collector.

        Returns:
            Collector containing the info, warning and error issues.
        """

    @_Classproperty
    def data_nodes(cls) -> Dict[str, DataNodeConfig]:
        """Return all data node configurations grouped by id in a dictionary.

        `Config.data_nodes()` is an alias for `Config.sections["DATA_NODE"]`
        """

    @staticmethod
    def configure_data_node(
        id: str,
        storage_type: str = ...,
        scope: Scope = ...,
        **properties: Dict[str, Any],
    ) -> DataNodeConfig:
        """Configure a new data node configuration.
        Parameters:
            id (str): The unique identifier of the new data node configuration.
            storage_type (str): The data node configuration storage type. The possible values
                are _"pickle"_ (which the default value, unless it has been overloaded by the
                _storage_type_ value set in the default data node configuration
                (see `(Config.)configure_default_data_node()^`)), _"csv"_, _"excel"_, _"sql_table"_, _"sql"_, _"json"_,
                _"parquet"_, _"mongo_collection"_, _"in_memory"_, or _"generic"_.
            scope (Scope^): The scope of the data node configuration. The default value is
                `Scope.SCENARIO` (or the one specified in
                `(Config.)configure_default_data_node()^`).
            **properties (Dict[str, Any]): A keyworded variable length list of additional
                arguments.
        Returns:
            `DataNodeConfig^`: The new data node configuration.
        """

    @staticmethod
    def configure_default_data_node(
        storage_type: str,
        scope: Scope = ...,
        **properties: Dict[str, Any],
    ) -> DataNodeConfig:
        """Configure the default values for data node configurations.
        This function creates the _default data node configuration_ object,
        where all data node configuration objects will find their default
        values when needed.
        Parameters:
            storage_type (str): The default storage type for all data node configurations.
                The possible values are _"pickle"_ (the default value), _"csv"_, _"excel"_,
                _"sql"_, _"mongo_collection"_, _"in_memory"_, _"json"_, _"parquet"_ or _"generic"_.
            scope (Scope^): The default scope for all data node configurations.
                The default value is `Scope.SCENARIO`.
            **properties (Dict[str, Any]): A keyworded variable length list of additional
                arguments.
        Returns:
            `DataNodeConfig^`: The default data node configuration.
        """

    @staticmethod
    def configure_csv_data_node(
        id: str,
        default_path: str = ...,
        has_header: bool = ...,
        exposed_type=...,
        scope: Scope = ...,
        **properties: Dict[str, Any],
    ) -> DataNodeConfig:
        """Configure a new CSV data node configuration.
        Parameters:
            id (str): The unique identifier of the new CSV data node configuration.
            default_path (str): The default path of the CSV file.
            has_header (bool): If True, indicates that the CSV file has a header.
            exposed_type: The exposed type of the data read from CSV file. The default value is `pandas`.
            scope (Scope^): The scope of the CSV data node configuration. The default value
                is `Scope.SCENARIO`.
            **properties (Dict[str, Any]): A keyworded variable length list of additional
                arguments.
        Returns:
            `DataNodeConfig^`: The new CSV data node configuration.
        """

    @staticmethod
    def configure_json_data_node(
        id: str,
        default_path: str = ...,
        encoder: json.JSONEncoder = ...,
        decoder: json.JSONDecoder = ...,
        scope: Scope = ...,
        **properties: Dict[str, Any],
    ) -> DataNodeConfig:
        """Configure a new JSON data node configuration.
        Parameters:
            id (str): The unique identifier of the new JSON data node configuration.
            default_path (str): The default path of the JSON file.
            encoder (json.JSONEncoder): The JSON encoder used to write data into the JSON file.
            decoder (json.JSONDecoder): The JSON decoder used to read data from the JSON file.
            scope (Scope^): The scope of the JSON data node configuration. The default value
                is `Scope.SCENARIO`.
            **properties (Dict[str, Any]): A keyworded variable length list of additional
                arguments.
        Returns:
            `DataNodeConfig^`: The new JSON data node configuration.
        """

    @staticmethod
    def configure_parquet_data_node(
        id: str,
        default_path: str = ...,
        exposed_type=...,
        engine: Optional[str] = ...,
        compression: Optional[str] = ...,
        read_kwargs: Dict = ...,
        write_kwargs: Dict = ...,
        scope: Scope = ...,
        **properties: Dict[str, Any],
    ) -> DataNodeConfig:
        """Configure a new Parquet data node configuration.
        Parameters:
            id (str): The unique identifier of the new Parquet data node configuration.
            default_path (str): The default path of the Parquet file.
            exposed_type: The exposed type of the data read from Parquet file. The default value is `pandas`.
            engine (Optional[str]): Parquet library to use. Possible values are _"fastparquet"_ or _"pyarrow"_.
                The default value is _"pyarrow"_.
            compression (Optional[str]): Name of the compression to use. Use None for no compression.
                `{'snappy', 'gzip', 'brotli', None}`, default `'snappy'`.
            read_kwargs (Optional[Dict]): Additional parameters passed to the `pandas.read_parquet` method.
            write_kwargs (Optional[Dict]): Additional parameters passed to the `pandas.DataFrame.write_parquet` method.
                The parameters in "read_kwargs" and "write_kwargs" have a **higher precedence** than the top-level parameters which are also
                passed to Pandas.
            scope (Scope^): The scope of the Parquet data node configuration. The default value
                is `Scope.SCENARIO`.
            **properties (Dict[str, Any]): A keyworded variable length list of additional
                arguments.
        Returns:
            `DataNodeConfig^`: The new Parquet data node configuration.
        """

    @staticmethod
    def configure_sql_table_data_node(
        id: str,
        db_username: str,
        db_password: str,
        db_name: str,
        db_engine: str,
        table_name: str = ...,
        db_port: int = ...,
        db_host: str = ...,
        db_driver: str = ...,
        db_extra_args: Dict[str, Any] = ...,
        exposed_type=...,
        scope: Scope = ...,
        **properties: Dict[str, Any],
    ) -> DataNodeConfig:
        """Configure a new SQL table data node configuration.
        Parameters:
            id (str): The unique identifier of the new SQL data node configuration.
            db_username (str): The database username.
            db_password (str): The database password.
            db_name (str): The database name.
            db_host (str): The database host. The default value is _"localhost"_.
            db_engine (str): The database engine. Possible values are _"sqlite"_, _"mssql"_, _"mysql"_, or _"postgresql"_.
            db_driver (str): The database driver. The default value is
                _"ODBC Driver 17 for SQL Server"_.
            db_port (int): The database port. The default value is 1433.
            db_extra_args (Dict[str, Any]): A dictionary of additional arguments to be passed into database
                connection string.
            table_name (str): The name of the SQL table.
            exposed_type: The exposed type of the data read from SQL query. The default value is `pandas`.
            scope (Scope^): The scope of the SQL data node configuration. The default value is
                `Scope.SCENARIO`.
            **properties (Dict[str, Any]): A keyworded variable length list of additional
                arguments.
        Returns:
            `DataNodeConfig^`: The new SQL data node configuration.
        """

    @staticmethod
    def configure_sql_data_node(
        id: str,
        db_username: str,
        db_password: str,
        db_name: str,
        db_engine: str,
        db_port: int = ...,
        db_host: str = ...,
        db_driver: str = ...,
        db_extra_args: Dict[str, Any] = ...,
        read_query: str = ...,
        write_query_builder: Callable = ...,
        exposed_type=...,
        scope: Scope = ...,
        **properties: Dict[str, Any],
    ) -> DataNodeConfig:
        """Configure a new SQL data node configuration.
        Parameters:
            id (str): The unique identifier of the new SQL data node configuration.
            db_username (str): The database username.
            db_password (str): The database password.
            db_name (str): The database name.
            db_engine (str): The database engine. Possible values are _"sqlite"_, _"mssql"_, _"mysql"_, or _"postgresql"_.
            db_port (int): The database port. The default value is 1433.
            db_host (str): The database host. The default value is _"localhost"_.
            db_driver (str): The database driver. The default value is
                _"ODBC Driver 17 for SQL Server"_.
            db_extra_args (Dict[str, Any]): A dictionary of additional arguments to be passed into database
                connection string.
            read_query (str): The SQL query string used to read the data from the database.
            write_query_builder (Callable): A callback function that takes the data as an input parameter and returns a list of SQL queries.
            exposed_type: The exposed type of the data read from SQL query. The default value is `pandas`.
            scope (Scope^): The scope of the SQL data node configuration. The default value is
                `Scope.SCENARIO`.
            **properties (Dict[str, Any]): A keyworded variable length list of additional
                arguments.
        Returns:
            `DataNodeConfig^`: The new SQL data node configuration.
        """

    @staticmethod
    def configure_mongo_collection_data_node(
        id: str,
        db_name: str,
        collection_name: str,
        custom_document: Any = ...,
        db_username: str = ...,
        db_password: str = ...,
        db_host: str = ...,
        db_port: int = ...,
        db_extra_args: Dict[str, Any] = ...,
        scope: Scope = ...,
        **properties: Dict[str, Any],
    ) -> DataNodeConfig:
        """Configure a new Mongo collection data node configuration.
        Parameters:
            id (str): The unique identifier of the new Mongo collection data node configuration.
            db_name (str): The database name.
            collection_name (str): The collection in the database to read from and to write the data to.
            custom_document (Any): The custom document class to store, encode, and decode data when reading and writing to a Mongo collection.
                The custom_document can have optional `decode` method to decode data in the Mongo collection to a custom object,
                and `encode` method to encode the object's properties to the Mongo collection when writing.
            db_username (str): The database username.
            db_password (str): The database password.
            db_host (str): The database host. The default value is _"localhost"_.
            db_port (int): The database port. The default value is 27017.
            db_extra_args (Dict[str, Any]): A dictionary of additional arguments to be passed into database connection string.
            scope (Scope^): The scope of the Mongo collection data node configuration. The default value is
                `Scope.SCENARIO`.
            **properties (Dict[str, Any]): A keyworded variable length list of additional
                arguments.
        Returns:
            `DataNodeConfig^`: The new Mongo collection data node configuration.
        """

    @staticmethod
    def configure_in_memory_data_node(
        id: str,
        default_data: Optional[Any] = ...,
        scope: Scope = ...,
        **properties: Dict[str, Any],
    ) -> DataNodeConfig:
        """Configure a new _in_memory_ data node configuration.
        Parameters:
            id (str): The unique identifier of the new in_memory data node configuration.
            default_data (Optional[Any]): The default data of the data nodes instantiated from
                this in_memory data node configuration.
            scope (Scope^): The scope of the in_memory data node configuration. The default
                value is `Scope.SCENARIO`.
            **properties (Dict[str, Any]): A keyworded variable length list of additional
                arguments.
        Returns:
            `DataNodeConfig^`: The new _in_memory_ data node configuration.
        """

    @staticmethod
    def configure_pickle_data_node(
        id: str,
        default_data: Optional[Any] = ...,
        scope: Scope = ...,
        **properties: Dict[str, Any],
    ) -> DataNodeConfig:
        """Configure a new pickle data node configuration.
        Parameters:
            id (str): The unique identifier of the new pickle data node configuration.
            default_data (Optional[Any]): The default data of the data nodes instantiated from
                this pickle data node configuration.
            scope (Scope^): The scope of the pickle data node configuration. The default value
                is `Scope.SCENARIO`.
            **properties (Dict[str, Any]): A keyworded variable length list of additional
                arguments.
        Returns:
            `DataNodeConfig^`: The new pickle data node configuration.
        """

    @staticmethod
    def configure_excel_data_node(
        id: str,
        default_path: str = ...,
        has_header: bool = True,
        sheet_name: Union[List[str], str] = ...,
        exposed_type=...,
        scope: Scope = ...,
        **properties: Dict[str, Any],
    ) -> DataNodeConfig:
        """Configure a new Excel data node configuration.
        Parameters:
            id (str): The unique identifier of the new Excel data node configuration.
            default_path (str): The path of the Excel file.
            has_header (bool): If True, indicates that the Excel file has a header.
            sheet_name (Union[List[str], str]): The list of sheet names to be used. This
                can be a unique name.
            exposed_type: The exposed type of the data read from Excel file. The default value is `pandas`.
            scope (Scope^): The scope of the Excel data node configuration. The default
                value is `Scope.SCENARIO`.
            **properties (Dict[str, Any]): A keyworded variable length list of additional
                arguments.
        Returns:
            `DataNodeConfig^`: The new CSV data node configuration.
        """

    @staticmethod
    def configure_generic_data_node(
        id: str,
        read_fct: Callable = ...,
        write_fct: Callable = ...,
        read_fct_params: List = ...,
        write_fct_params: List = ...,
        scope: Scope = ...,
        **properties: Dict[str, Any],
    ) -> DataNodeConfig:
        """Configure a new generic data node configuration.
        Parameters:
            id (str): The unique identifier of the new generic data node configuration.
            read_fct (Optional[Callable]): The Python function called to read the data.
            write_fct (Optional[Callable]): The Python function called to write the data.
                The provided function must have at least one parameter that receives the data
                to be written.
            read_fct_params (Optional[List]): The parameters that are passed to _read_fct_
                to read the data.
            write_fct_params (Optional[List]): The parameters that are passed to _write_fct_
                to write the data.
            scope (Optional[Scope^]): The scope of the Generic data node configuration.
                The default value is `Scope.SCENARIO`.
            **properties (Dict[str, Any]): A keyworded variable length list of additional
                arguments.
        Returns:
            `DataNodeConfig^`: The new Generic data node configuration.
        """

    @_Classproperty
    def job_config(cls) -> JobConfig:
        """Return the job execution configuration `JobConfig^`."""

    @staticmethod
    def configure_job_executions(
        mode: str = ...,
        nb_of_workers: Union[int, str] = ...,
        max_nb_of_workers: Union[int, str] = ...,
        **properties: Dict[str, Any],
    ) -> JobConfig:
        """Configure job execution.
        Parameters:
            mode (Optional[str]): The job execution mode.
                Possible values are: _"standalone"_ (the default value) or
                _"development"_.
            max_nb_of_workers (Optional[int, str]): Parameter used only in default _"standalone"_ mode. The maximum
                number of jobs able to run in parallel. The default value is 1.<br/>
                A string can be provided to dynamically set the value using an environment
                variable. The string must follow the pattern: `ENV[&lt;env_var&gt;]` where
                `&lt;env_var&gt;` is the name of environment variable.
            nb_of_workers (Optional[int, str]): Deprecated. Use max_nb_of_workers instead.
        Returns:
            `JobConfig^`: The job execution configuration.
        """

    @_Classproperty
    def pipelines(cls) -> Dict[str, PipelineConfig]:
        """Return all pipeline configurations grouped by id in a dictionary.

        `Config.pipelines()` is an alias for `Config.sections["PIPELINE"]`
        """

    @staticmethod
    def configure_pipeline(id: str, task_configs: Union[TaskConfig, List[TaskConfig]], **properties: Dict[str, Any]) -> PipelineConfig:  # type: ignore
        """Configure a new pipeline configuration.
        Parameters:
            id (str): The unique identifier of the new pipeline configuration.
            task_configs (Union[TaskConfig^, List[TaskConfig^]]): The list of the task
                configurations that make this new pipeline. This can be a single task
                configuration object is this pipeline holds a single task.
            **properties (Dict[str, Any]): A keyworded variable length list of additional
                arguments.
        Returns:
            `PipelineConfig^`: The new pipeline configuration.
        """

    @staticmethod
    def configure_default_pipeline(task_configs: Union[TaskConfig, List[TaskConfig]], **properties: Dict[str, Any]) -> PipelineConfig:  # type: ignore
        """Configure the default values for pipeline configurations.
        This function creates the _default pipeline configuration_ object,
        where all pipeline configuration objects will find their default
        values when needed.
        Parameters:
            task_configs (Union[TaskConfig^, List[TaskConfig^]]): The list of the task
                configurations that make the default pipeline configuration. This can be
                a single task configuration object is this pipeline holds a single task.
            **properties (Dict[str, Any]): A keyworded variable length list of additional
                arguments.
        Returns:
            `PipelineConfig^`: The default pipeline configuration.
        """

    @_Classproperty
    def scenarios(cls) -> Dict[str, ScenarioConfig]:
        """Return all scenario configurations grouped by id in a dictionary.

        `Config.scenarios()` is an alias for `Config.sections["SCENARIO"]`
        """

    @staticmethod
    def configure_scenario(
        id: str,
        pipeline_configs: List[PipelineConfig],  # type: ignore
        frequency: Optional[Frequency] = ...,
        comparators: Optional[Dict[str, Union[List[Callable], Callable]]] = ...,
        **properties: Dict[str, Any],
    ) -> ScenarioConfig:
        """Configure a new scenario configuration.
        Parameters:
            id (str): The unique identifier of the new scenario configuration.
            pipeline_configs (List[PipelineConfig^]): The list of pipeline configurations used
                by this new scenario configuration.
            frequency (Optional[Frequency^]): The scenario frequency.
                It corresponds to the recurrence of the scenarios instantiated from this
                configuration. Based on this frequency each scenario will be attached to the
                relevant cycle.
            comparators (Optional[Dict[str, Union[List[Callable], Callable]]]): The list of
                functions used to compare scenarios. A comparator function is attached to a
                scenario's data node configuration. The key of the dictionary parameter
                corresponds to the data node configuration id. During the scenarios'
                comparison, each comparator is applied to all the data nodes instantiated from
                the data node configuration attached to the comparator. See
                `(taipy.)compare_scenarios()^` more more details.
            **properties (Dict[str, Any]): A keyworded variable length list of additional
                arguments.
        Returns:
            `ScenarioConfig^`: The new scenario configuration.
        """

    @staticmethod
    def configure_default_scenario(
        pipeline_configs: List[PipelineConfig],  # type: ignore
        frequency: Optional[Frequency] = ...,
        comparators: Optional[Dict[str, Union[List[Callable], Callable]]] = ...,
        **properties: Dict[str, Any],
    ) -> ScenarioConfig:
        """Configure the default values for scenario configurations.
        This function creates the _default scenario configuration_ object,
        where all scenario configuration objects will find their default
        values when needed.
        Parameters:
            pipeline_configs (List[PipelineConfig^]): The list of pipeline configurations used
                by this scenario configuration.
            frequency (Optional[Frequency^]): The scenario frequency.
                It corresponds to the recurrence of the scenarios instantiated from this
                configuration. Based on this frequency each scenario will be attached to
                the relevant cycle.
            comparators (Optional[Dict[str, Union[List[Callable], Callable]]]): The list of
                functions used to compare scenarios. A comparator function is attached to a
                scenario's data node configuration. The key of the dictionary parameter
                corresponds to the data node configuration id. During the scenarios'
                comparison, each comparator is applied to all the data nodes instantiated from
                the data node configuration attached to the comparator. See
                `taipy.compare_scenarios()^` more more details.
            **properties (Dict[str, Any]): A keyworded variable length list of additional
                arguments.
        Returns:
            `ScenarioConfig^`: The default scenario configuration.
        """

    @staticmethod
    def configure_scenario_from_tasks(
        id: str,
        task_configs: List[TaskConfig],  # type: ignore
        frequency: Optional[Frequency] = ...,
        comparators: Optional[Dict[str, Union[List[Callable], Callable]]] = ...,
        pipeline_id: Optional[str] = ...,
        **properties: Dict[str, Any],
    ) -> ScenarioConfig:
        """Configure a new scenario configuration made of a single new pipeline configuration.
        A new pipeline configuration is created as well. If _pipeline_id_ is not provided,
        the new pipeline configuration identifier is set to the scenario configuration identifier
        post-fixed by '_pipeline'.
        Parameters:
            id (str): The unique identifier of the scenario configuration.
            task_configs (List[TaskConfig^]): The list of task configurations used by the
                new pipeline configuration that is created.
            frequency (Optional[Frequency^]): The scenario frequency.
                It corresponds to the recurrence of the scenarios instantiated from this
                configuration. Based on this frequency each scenario will be attached to the
                relevant cycle.
            comparators (Optional[Dict[str, Union[List[Callable], Callable]]]): The list of
                functions used to compare scenarios. A comparator function is attached to a
                scenario's data node configuration. The key of the dictionary parameter
                corresponds to the data node configuration id. During the scenarios'
                comparison, each comparator is applied to all the data nodes instantiated from
                the data node configuration attached to the comparator. See
                `(taipy.)compare_scenarios()` more more details.
            pipeline_id (str): The identifier of the new pipeline configuration to be
                configured.
            **properties (Dict[str, Any]): A keyworded variable length list of additional
                arguments.
        Returns:
            `ScenarioConfig^`: The new scenario configuration.
        """

    @_Classproperty
    def tasks(cls) -> Dict[str, TaskConfig]:
        """Return all task configurations grouped by id in a dictionary.

        `Config.tasks()` is an alias for `Config.sections["TASK"]`
        """

    @staticmethod
    def configure_task(
        id: str,
        function: Callable,
        input: Optional[Union[DataNodeConfig, List[DataNodeConfig]]] = ...,  # type: ignore
        output: Optional[Union[DataNodeConfig, List[DataNodeConfig]]] = ...,  # type: ignore
        skippable: Optional[bool] = ...,  # type: ignore
        **properties: Dict[str, Any],
    ) -> TaskConfig:
        """Configure a new task configuration.
        Parameters:
            id (str): The unique identifier of this task configuration.
            function (Callable): The python function called by Taipy to run the task.
            input (Optional[Union[DataNodeConfig^, List[DataNodeConfig^]]]): The list of the
                function input data node configurations. This can be a unique data node
                configuration if there is a single input data node, or None if there are none.
            output (Optional[Union[DataNodeConfig^, List[DataNodeConfig^]]]): The list of the
                function output data node configurations. This can be a unique data node
                configuration if there is a single output data node, or None if there are none.
            skippable (bool): If True, indicates that the task can be skipped if no change has
                been made on inputs. The default value is _False_.
            **properties (Dict[str, Any]): A keyworded variable length list of additional
                arguments.
        Returns:
            `TaskConfig^`: The new task configuration.
        """

    @staticmethod
    def configure_default_task(
        function: Callable,
        input: Optional[Union[DataNodeConfig, List[DataNodeConfig]]] = ...,  # type: ignore
        output: Optional[Union[DataNodeConfig, List[DataNodeConfig]]] = ...,  # type: ignore
        skippable: Optional[bool] = ...,  # type: ignore
        **properties: Dict[str, Any],
    ) -> TaskConfig:
        """Configure the default values for task configurations.
        This function creates the _default task configuration_ object,
        where all task configuration objects will find their default
        values when needed.
        Parameters:
            function (Callable): The python function called by Taipy to run the task.
            input (Optional[Union[DataNodeConfig^, List[DataNodeConfig^]]]): The list of the
                input data node configurations. This can be a unique data node
                configuration if there is a single input data node, or None if there are none.
            output (Optional[Union[DataNodeConfig^, List[DataNodeConfig^]]]): The list of the
                output data node configurations. This can be a unique data node
                configuration if there is a single output data node, or None if there are none.
            skippable (bool): If True, indicates that the task can be skipped if no change has
                been made on inputs. The default value is _False_.
            **properties (Dict[str, Any]): A keyworded variable length list of additional
                arguments.
        Returns:
            `TaskConfig^`: The default task configuration.
        """
