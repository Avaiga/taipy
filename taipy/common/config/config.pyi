# Copyright 2021-2024 Avaiga Private Limited
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
from datetime import timedelta
from typing import Any, Callable, Dict, List, Optional, Union

from taipy.common.config._config import _Config
from taipy.core.config import CoreSection, DataNodeConfig, JobConfig, ScenarioConfig, TaskConfig

from .checker.issue_collector import IssueCollector
from .common._classproperty import _Classproperty
from .common._config_blocker import _ConfigBlocker
from .common.frequency import Frequency
from .common.scope import Scope
from .global_app.global_app_config import GlobalAppConfig
from .section import Section
from .unique_section import UniqueSection

class Config:
    """Singleton class that manages the configuration of a Taipy application.

    The `Config` singleton is the main class to use for configuring a Taipy application.
    In particular, this class provides:

    1. Various methods to configure the application's behavior

        The Config class provides various methods to configure the application. Each method adds
        a specific section to the configuration and returns it.

        ??? example "Most frequently used configuration methods"

            ```python
            from taipy import Config

            def by_two(x: int):
                return x * 2

            input_cfg = Config.configure_data_node("my_input")
            result_cfg = Config.configure_data_node("my_result")
            task_cfg = Config.configure_task("my_double", function=by_two, input=input_cfg, output=result_cfg)
            scenario_cfg = Config.configure_scenario("my_scenario", task_configs=[task_cfg])

            Config.load("config.toml") # Load a configuration file
            ```

        ??? example "Advanced use case"

            The configuration can be done in three ways: Python code, configuration files, or
            environment variables. All configuration manners are ultimately merged (overriding the previous
            way) to create a final applied configuration. Please refer to the
            [advanced configuration](../../../../../../userman/advanced_features/configuration/advanced-config.md)
            section from the user manual for more details.

    2. Attributes and methods to retrieve the configuration values.

        Once the configuration is done, you can retrieve the configuration values using the exposed
        attributes.

        ??? Example "Retrieve configuration values"

            ```python
            from taipy import Config

            global_cfg = Config.global_config  # Retrieve the global application configuration
            data_node_cfgs = Config.data_nodes  # Retrieve all data node configurations
            scenario_cfgs = Config.scenarios  # Retrieve all scenario configurations
            ```

    3. A few methods to manage the configuration:

        The Config class also provides a few methods to manage the configuration.

        ??? example "Manage the configuration"

            - *Check the configuration for issues*: Use the `Config.check()^` method to check the
                configuration. It returns an `IssueCollector^` containing all the
                 `Issue^`s found. The issues are logged to the console for debugging.
            - *Block the configuration update*: Use the `Config.block_update()^` method to forbid
                any update on the configuration. This can be useful when you want to ensure that
                the configuration is not modified at run time. Note that running the `Orchestrator^`
                service` automatically blocks the configuration update.
            - *Unblock the configuration update*: Use the `Config.unblock_update()^` method to allow
                again the update on the configuration.
            - *Backup the configuration*: Use the `Config.backup()^` method to back up as a TOML
                file the applied configuration. The applied configuration backed up is the result
                of the compilation of the three possible configuration methods that overrides each
                others.
            - *Restore the configuration*: Use the `Config.restore()^` method to restore a TOML
                configuration file and replace the current applied configuration.
            - *Export the configuration*: Use the `Config.export()^` method to export as a TOML file
                the Python code configuration.
            - *Load the configuration*: Use the `Config.load()^` method to load a TOML configuration
                file and replace the current Python configuration.
            - *Override the configuration*: Use the `Config.override()^` method to load a TOML
                configuration file and override the current Python configuration.
    """
    @_Classproperty
    def unique_sections(cls) -> Dict[str, UniqueSection]:
        """A dictionary containing all unique sections."""

    @_Classproperty
    def sections(cls) -> Dict[str, Dict[str, Section]]:
        """A dictionary containing all non-unique sections."""

    @_Classproperty
    def global_config(cls) -> GlobalAppConfig:
        """configuration values related to the global application as a `GlobalAppConfig^`."""

    @classmethod
    @_ConfigBlocker._check()
    def load(cls, filename: str) -> None:
        """Load a configuration file.

        The current Python configuration is replaced and the Config compilation is triggered.

        Parameters:
            filename (Union[str, Path]): The path of the toml configuration file to load.
        """

    @classmethod
    def export(cls, filename: str) -> None:
        """Export a configuration.

        The export is done in a toml file. The exported configuration is taken
        from the Python code configuration.

        Note:
            If *filename* already exists, it is overwritten.

        Parameters:
            filename (Union[str, Path]): The path of the file to export.
        """

    @classmethod
    def backup(cls, filename: str) -> None:
        """Backup a configuration.

        The backup is done in a toml file.

        The backed up configuration is a compilation from the three possible methods to configure
        the application: the Python code configuration, the file configuration and the environment
        configuration.

        Note:
            If *filename* already exists, it is overwritten.

        Parameters:
            filename (Union[str, Path]): The path of the file to export.
        """

    @classmethod
    @_ConfigBlocker._check()
    def restore(cls, filename: str) -> None:
        """Restore a configuration file and replace the current applied configuration.

        Parameters:
            filename (Union[str, Path]): The path of the toml configuration file to load.
        """

    @classmethod
    @_ConfigBlocker._check()
    def override(cls, filename: str) -> None:
        """Load a configuration from a file and overrides the current config.

        Parameters:
            filename (Union[str, Path]): The path of the toml configuration file to load.
        """

    @classmethod
    def block_update(cls) -> None:
        """Block update on the configuration signgleton."""

    @classmethod
    def unblock_update(cls) -> None:
        """Unblock update on the configuration signgleton."""

    @classmethod
    @_ConfigBlocker._check()
    def configure_global_app(cls, **properties) -> GlobalAppConfig:
        """Configure the global application.

        Parameters:
            **properties (Dict[str, Any]): A dictionary of additional properties.

        Returns:
            The global application configuration.
        """

    @classmethod
    def check(cls) -> IssueCollector:
        """Check configuration.

        This method logs issue messages and returns an issue collector.

        Returns:
            Collector containing the info, warning and error issues.

        Raises:
            SystemExit: If configuration errors are found, the application
                exits with an error message.
        """

    @classmethod
    @_ConfigBlocker._check()
    def _register_default(cls, default_section: Section) -> None:
        """"""

    @classmethod
    @_ConfigBlocker._check()
    def _register(cls, section) -> None:
        """"""

    @classmethod
    def _override_env_file(cls) -> None:
        """"""

    @classmethod
    def _compile_configs(cls) -> None:
        """"""

    @classmethod
    def _to_json(cls, _config: _Config) -> str:
        """"""

    @classmethod
    def _from_json(cls, config_as_str: str) -> _Config:
        """"""

    @_Classproperty
    def job_config(cls) -> JobConfig:
        """"""

    @_Classproperty
    def data_nodes(cls) -> Dict[str, DataNodeConfig]:
        """"""

    @_Classproperty
    def tasks(cls) -> Dict[str, TaskConfig]:
        """"""

    @_Classproperty
    def scenarios(cls) -> Dict[str, ScenarioConfig]:
        """"""

    @_Classproperty
    def core(cls) -> Dict[str, CoreSection]:
        """"""

    @staticmethod
    def configure_scenario(
        id: str,
        task_configs: Optional[List[TaskConfig]] = None,
        additional_data_node_configs: Optional[List[DataNodeConfig]] = None,
        frequency: Optional[Frequency] = None,
        comparators: Optional[Dict[str, Union[List[Callable], Callable]]] = None,
        sequences: Optional[Dict[str, List[TaskConfig]]] = None,
        **properties,
    ) -> "ScenarioConfig":
        """Configure a new scenario configuration.

        Parameters:
            id (str): The unique identifier of the new scenario configuration.
            task_configs (Optional[List[TaskConfig^]]): The list of task configurations used by this
                scenario configuration. The default value is None.
            additional_data_node_configs (Optional[List[DataNodeConfig^]]): The list of additional data nodes
                related to this scenario configuration. The default value is None.
            frequency (Optional[Frequency^]): The scenario frequency.<br/>
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
            sequences (Optional[Dict[str, List[TaskConfig]]]): Dictionary of sequence descriptions.
                The default value is None.
            **properties (dict[str, any]): A keyworded variable length list of additional arguments.

        Returns:
            The new scenario configuration.
        """

    @staticmethod
    def set_default_scenario_configuration(
        task_configs: Optional[List[TaskConfig]] = None,
        additional_data_node_configs: List[DataNodeConfig] = None,
        frequency: Optional[Frequency] = None,
        comparators: Optional[Dict[str, Union[List[Callable], Callable]]] = None,
        sequences: Optional[Dict[str, List[TaskConfig]]] = None,
        **properties,
    ) -> "ScenarioConfig":
        """Set the default values for scenario configurations.

        This function creates the *default scenario configuration* object,
        where all scenario configuration objects will find their default
        values when needed.

        Parameters:
            task_configs (Optional[List[TaskConfig^]]): The list of task configurations used by this
                scenario configuration.
            additional_data_node_configs (Optional[List[DataNodeConfig^]]): The list of additional data nodes
                related to this scenario configuration.
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
            sequences (Optional[Dict[str, List[TaskConfig]]]): Dictionary of sequences. The default value is None.
            **properties (dict[str, any]): A keyworded variable length list of additional arguments.

        Returns:
            The new default scenario configuration.
        """

    @staticmethod
    def set_default_data_node_configuration(
        storage_type: str, scope: Optional[Scope] = None, validity_period: Optional[timedelta] = None, **properties
    ) -> "DataNodeConfig":
        """Set the default values for data node configurations.

        This function creates the _default data node configuration_ object,
        where all data node configuration objects will find their default
        values when needed.

        Parameters:
            storage_type (str): The default storage type for all data node configurations.
                The possible values are *"pickle"* (the default value), *"csv"*, *"excel"*,
                *"sql"*, *"mongo_collection"*, *"in_memory"*, *"json"*, *"parquet"*, *"generic"*,
                or *"s3_object"*.
            scope (Optional[Scope^]): The default scope for all data node configurations.<br/>
                The default value is `Scope.SCENARIO`.
            validity_period (Optional[timedelta]): The duration since the last edit date for which the data node can be
                considered up-to-date. Once the validity period has passed, the data node is considered stale and
                relevant tasks will run even if they are skippable (see the Task configuration
                [page](../../../../../../userman/scenario_features/task-orchestration/scenario-config.md#from-task-configurations)
                for more details).
                If *validity_period* is set to None, the data node is always up-to-date.
            **properties (dict[str, any]): A keyworded variable length list of additional arguments.

        Returns:
            The default data node configuration.
        """  # noqa: E501

    @classmethod
    def configure_data_node_from(
        cls,
        source_configuration: "DataNodeConfig",
        id: str,
        **properties,
    ) -> "DataNodeConfig":
        """Configure a new data node configuration from an existing one.

        Parameters:
            source_configuration (DataNodeConfig): The source data node configuration.
            id (str): The unique identifier of the new data node configuration.
            **properties (dict[str, any]): A keyworded variable length list of additional arguments.<br/>
                The default properties are the properties of the source data node configuration.

        Returns:
            The new data node configuration.
        """

    @classmethod
    def configure_data_node(
        cls,
        id: str,
        storage_type: Optional[str] = None,
        scope: Optional[Scope] = None,
        validity_period: Optional[timedelta] = None,
        **properties,
    ) -> "DataNodeConfig":
        """Configure a new data node configuration.

        Parameters:
            id (str): The unique identifier of the new data node configuration.
            storage_type (Optional[str]): The data node configuration storage type. The possible values
                are None (which is the default value of *"pickle"*, unless it has been overloaded by the
                *storage_type* value set in the default data node configuration
                (see `(Config.)set_default_data_node_configuration()^`)), *"pickle"*, *"csv"*, *"excel"*,
                *"sql_table"*, *"sql"*, *"json"*, *"parquet"*, *"mongo_collection"*, *"in_memory"*, or
                *"generic"*.
            scope (Optional[Scope^]): The scope of the data node configuration.<br/>
                The default value is `Scope.SCENARIO` (or the one specified in
                `(Config.)set_default_data_node_configuration()^`).
            validity_period (Optional[timedelta]): The duration since the last edit date for which the data node can be
                considered up-to-date. Once the validity period has passed, the data node is considered stale and
                relevant tasks will run even if they are skippable (see the Task configuration
                [page](../../../../../../userman/scenario_features/task-orchestration/scenario-config.md#from-task-configurations)
                for more details).
                If *validity_period* is set to None, the data node is always up-to-date.
            **properties (dict[str, any]): A keyworded variable length list of additional arguments.

        Returns:
            The new data node configuration.
        """  # noqa: E501

    @classmethod
    def configure_csv_data_node(
        cls,
        id: str,
        default_path: Optional[str] = None,
        encoding: Optional[str] = None,
        has_header: Optional[bool] = None,
        exposed_type: Optional[str] = None,
        scope: Optional[Scope] = None,
        validity_period: Optional[timedelta] = None,
        **properties,
    ) -> "DataNodeConfig":
        """Configure a new CSV data node configuration.

        Parameters:
            id (str): The unique identifier of the new CSV data node configuration.
            default_path (Optional[str]): The default path of the CSV file.
            encoding (Optional[str]): The encoding of the CSV file.
            has_header (Optional[bool]): If True, indicates that the CSV file has a header.
            exposed_type (Optional[str]): The exposed type of the data read from CSV file.<br/>
                The default value is `pandas`.
            scope (Optional[Scope^]): The scope of the CSV data node configuration.<br/>
                The default value is `Scope.SCENARIO`.
            validity_period (Optional[timedelta]): The duration since the last edit date for which the data node can be
                considered up-to-date. Once the validity period has passed, the data node is considered stale and
                relevant tasks will run even if they are skippable (see the Task configuration
                [page](../../../../../../userman/scenario_features/task-orchestration/scenario-config.md#from-task-configurations)
                for more details).
                If *validity_period* is set to None, the data node is always up-to-date.
            **properties (dict[str, any]): A keyworded variable length list of additional arguments.

        Returns:
            The new CSV data node configuration.
        """  # noqa: E501

    @classmethod
    def configure_json_data_node(
        cls,
        id: str,
        default_path: Optional[str] = None,
        encoding: Optional[str] = None,
        encoder: Optional[json.JSONEncoder] = None,
        decoder: Optional[json.JSONDecoder] = None,
        scope: Optional[Scope] = None,
        validity_period: Optional[timedelta] = None,
        **properties,
    ) -> "DataNodeConfig":
        """Configure a new JSON data node configuration.

        Parameters:
            id (str): The unique identifier of the new JSON data node configuration.
            default_path (Optional[str]): The default path of the JSON file.
            encoding (Optional[str]): The encoding of the JSON file.
            encoder (Optional[json.JSONEncoder]): The JSON encoder used to write data into the JSON file.
            decoder (Optional[json.JSONDecoder]): The JSON decoder used to read data from the JSON file.
            scope (Optional[Scope^]): The scope of the JSON data node configuration.<br/>
                The default value is `Scope.SCENARIO`.
            validity_period (Optional[timedelta]): The duration since the last edit date for which the data node can be
                considered up-to-date. Once the validity period has passed, the data node is considered stale and
                relevant tasks will run even if they are skippable (see the Task configuration
                [page](../../../../../../userman/scenario_features/task-orchestration/scenario-config.md#from-task-configurations)
                for more details).
                If *validity_period* is set to None, the data node is always up-to-date.
            **properties (dict[str, any]): A keyworded variable length list of additional arguments.

        Returns:
            The new JSON data node configuration.
        """  # noqa: E501

    @classmethod
    def configure_parquet_data_node(
        cls,
        id: str,
        default_path: Optional[str] = None,
        engine: Optional[str] = None,
        compression: Optional[str] = None,
        read_kwargs: Optional[Dict] = None,
        write_kwargs: Optional[Dict] = None,
        exposed_type: Optional[str] = None,
        scope: Optional[Scope] = None,
        validity_period: Optional[timedelta] = None,
        **properties,
    ) -> "DataNodeConfig":
        """Configure a new Parquet data node configuration.

        Parameters:
            id (str): The unique identifier of the new Parquet data node configuration.
            default_path (Optional[str]): The default path of the Parquet file.
            engine (Optional[str]): Parquet library to use. Possible values are *"fastparquet"* or
                *"pyarrow"*.<br/>
                The default value is *"pyarrow"*.
            compression (Optional[str]): Name of the compression to use. Possible values are *"snappy"*,
                *"gzip"*, *"brotli"*, or *"none"* (no compression). The default value is *"snappy"*.
            read_kwargs (Optional[dict]): Additional parameters passed to the `pandas.read_parquet()`
                function.
            write_kwargs (Optional[dict]): Additional parameters passed to the
                `pandas.DataFrame.write_parquet()` function.<br/>
                The parameters in *read_kwargs* and *write_kwargs* have a **higher precedence** than the
                top-level parameters which are also passed to Pandas.
            exposed_type (Optional[str]): The exposed type of the data read from Parquet file.<br/>
                The default value is `pandas`.
            scope (Optional[Scope^]): The scope of the Parquet data node configuration.<br/>
                The default value is `Scope.SCENARIO`.
            validity_period (Optional[timedelta]): The duration since the last edit date for which the data node can be
                considered up-to-date. Once the validity period has passed, the data node is considered stale and
                relevant tasks will run even if they are skippable (see the Task configuration
                [page](../../../../../../userman/scenario_features/task-orchestration/scenario-config.md#from-task-configurations)
                for more details).
                If *validity_period* is set to None, the data node is always up-to-date.
            **properties (dict[str, any]): A keyworded variable length list of additional arguments.

        Returns:
            The new Parquet data node configuration.
        """  # noqa: E501

    @classmethod
    def configure_excel_data_node(
        cls,
        id: str,
        default_path: Optional[str] = None,
        has_header: Optional[bool] = None,
        sheet_name: Optional[Union[List[str], str]] = None,
        exposed_type: Optional[str] = None,
        scope: Optional[Scope] = None,
        validity_period: Optional[timedelta] = None,
        **properties,
    ) -> "DataNodeConfig":
        """Configure a new Excel data node configuration.

        Parameters:
            id (str): The unique identifier of the new Excel data node configuration.
            default_path (Optional[str]): The path of the Excel file.
            has_header (Optional[bool]): If True, indicates that the Excel file has a header.
            sheet_name (Optional[Union[List[str], str]]): The list of sheet names to be used.
                This can be a unique name.
            exposed_type (Optional[str]): The exposed type of the data read from Excel file.<br/>
                The default value is `pandas`.
            scope (Optional[Scope^]): The scope of the Excel data node configuration.<br/>
                The default value is `Scope.SCENARIO`.
            validity_period (Optional[timedelta]): The duration since the last edit date for which the data node can be
                considered up-to-date. Once the validity period has passed, the data node is considered stale and
                relevant tasks will run even if they are skippable (see the Task configuration
                [page](../../../../../../userman/scenario_features/task-orchestration/scenario-config.md#from-task-configurations)
                for more details).
                If *validity_period* is set to None, the data node is always up-to-date.
            **properties (dict[str, any]): A keyworded variable length list of additional arguments.

        Returns:
            The new Excel data node configuration.
        """  # noqa: E501

    @classmethod
    def configure_generic_data_node(
        cls,
        id: str,
        read_fct: Optional[Callable] = None,
        write_fct: Optional[Callable] = None,
        read_fct_args: Optional[List] = None,
        write_fct_args: Optional[List] = None,
        scope: Optional[Scope] = None,
        validity_period: Optional[timedelta] = None,
        **properties,
    ) -> "DataNodeConfig":
        """Configure a new generic data node configuration.

        Parameters:
            id (str): The unique identifier of the new generic data node configuration.
            read_fct (Optional[Callable]): The Python function called to read the data.
            write_fct (Optional[Callable]): The Python function called to write the data.
                The provided function must have at least one parameter that receives the data to be written.
            read_fct_args (Optional[List]): The list of arguments that are passed to the function
                *read_fct* to read data.
            write_fct_args (Optional[List]): The list of arguments that are passed to the function
                *write_fct* to write the data.
            scope (Optional[Scope^]): The scope of the Generic data node configuration.<br/>
                The default value is `Scope.SCENARIO`.
            validity_period (Optional[timedelta]): The duration since the last edit date for which the data node can be
                considered up-to-date. Once the validity period has passed, the data node is considered stale and
                relevant tasks will run even if they are skippable (see the Task configuration
                [page](../../../../../../userman/scenario_features/task-orchestration/scenario-config.md#from-task-configurations)
                for more details).
                If *validity_period* is set to None, the data node is always up-to-date.
            **properties (dict[str, any]): A keyworded variable length list of additional arguments.

        Returns:
            The new Generic data node configuration.
        """  # noqa: E501

    @classmethod
    def configure_in_memory_data_node(
        cls,
        id: str,
        default_data: Optional[Any] = None,
        scope: Optional[Scope] = None,
        validity_period: Optional[timedelta] = None,
        **properties,
    ) -> "DataNodeConfig":
        """Configure a new *in-memory* data node configuration.

        Parameters:
            id (str): The unique identifier of the new in_memory data node configuration.
            default_data (Optional[any]): The default data of the data nodes instantiated from
                this in_memory data node configuration.
                If provided, note that the default_data will be stored as a configuration attribute.
                So it is designed to handle small data values like parameters, and it must be Json serializable.
            scope (Optional[Scope^]): The scope of the in_memory data node configuration.<br/>
                The default value is `Scope.SCENARIO`.
            validity_period (Optional[timedelta]): The duration since the last edit date for which the data node can be
                considered up-to-date. Once the validity period has passed, the data node is considered stale and
                relevant tasks will run even if they are skippable (see the Task configuration
                [page](../../../../../../userman/scenario_features/task-orchestration/scenario-config.md#from-task-configurations)
                for more details).
                If *validity_period* is set to None, the data node is always up-to-date.
            **properties (dict[str, any]): A keyworded variable length list of additional arguments.

        Returns:
            The new *in-memory* data node configuration.
        """  # noqa: E501

    @classmethod
    def configure_pickle_data_node(
        cls,
        id: str,
        default_path: Optional[str] = None,
        default_data: Optional[Any] = None,
        scope: Optional[Scope] = None,
        validity_period: Optional[timedelta] = None,
        **properties,
    ) -> "DataNodeConfig":
        """Configure a new pickle data node configuration.

        Parameters:
            id (str): The unique identifier of the new pickle data node configuration.
            default_path (Optional[str]): The path of the pickle file.
            default_data (Optional[any]): The default data of the data nodes instantiated from
                this pickle data node configuration.
                If provided, note that the default_data will be stored as a configuration attribute.
                So it is designed to handle small data values like parameters, and it must be Json serializable.
            scope (Optional[Scope^]): The scope of the pickle data node configuration.<br/>
                The default value is `Scope.SCENARIO`.
            validity_period (Optional[timedelta]): The duration since the last edit date for which the data node can be
                considered up-to-date. Once the validity period has passed, the data node is considered stale and
                relevant tasks will run even if they are skippable (see the Task configuration
                [page](../../../../../../userman/scenario_features/task-orchestration/scenario-config.md#from-task-configurations)
                for more details).
                If *validity_period* is set to None, the data node is always up-to-date.
            **properties (dict[str, any]): A keyworded variable length list of additional arguments.

        Returns:
            The new pickle data node configuration.
        """  # noqa: E501

    @classmethod
    def configure_sql_table_data_node(
        cls,
        id: str,
        db_name: str,
        db_engine: str,
        table_name: str,
        db_username: Optional[str] = None,
        db_password: Optional[str] = None,
        db_host: Optional[str] = None,
        db_port: Optional[int] = None,
        db_driver: Optional[str] = None,
        sqlite_folder_path: Optional[str] = None,
        sqlite_file_extension: Optional[str] = None,
        db_extra_args: Optional[Dict[str, Any]] = None,
        exposed_type: Optional[str] = None,
        scope: Optional[Scope] = None,
        validity_period: Optional[timedelta] = None,
        **properties,
    ) -> "DataNodeConfig":
        """Configure a new SQL table data node configuration.

        Parameters:
            id (str): The unique identifier of the new SQL data node configuration.
            db_name (str): The database name, or the name of the SQLite database file.
            db_engine (str): The database engine. Possible values are *"sqlite"*, *"mssql"*, *"mysql"*,
                or *"postgresql"*.
            table_name (str): The name of the SQL table.
            db_username (Optional[str]): The database username. Required by the *"mssql"*, *"mysql"*, and
                *"postgresql"* engines.
            db_password (Optional[str]): The database password. Required by the *"mssql"*, *"mysql"*, and
                *"postgresql"* engines.
            db_host (Optional[str]): The database host.<br/>
                The default value is "localhost".
            db_port (Optional[int]): The database port.<br/>
                The default value is 1433.
            db_driver (Optional[str]): The database driver.
            sqlite_folder_path (Optional[str]): The path to the folder that contains SQLite file.<br/>
                The default value is the current working folder.
            sqlite_file_extension (Optional[str]): The file extension of the SQLite file.<br/>
                The default value is ".db".
            db_extra_args (Optional[dict[str, any]]): A dictionary of additional arguments to be passed
                into database connection string.
            exposed_type (Optional[str]): The exposed type of the data read from SQL table.<br/>
                The default value is "pandas".
            scope (Optional[Scope^]): The scope of the SQL data node configuration.<br/>
                The default value is `Scope.SCENARIO`.
            validity_period (Optional[timedelta]): The duration since the last edit date for which the data node can be
                considered up-to-date. Once the validity period has passed, the data node is considered stale and
                relevant tasks will run even if they are skippable (see the Task configuration
                [page](../../../../../../userman/scenario_features/task-orchestration/scenario-config.md#from-task-configurations)
                for more details).
                If *validity_period* is set to None, the data node is always up-to-date.
            **properties (dict[str, any]): A keyworded variable length list of additional arguments.

        Returns:
            The new SQL data node configuration.
        """  # noqa: E501

    @classmethod
    def configure_sql_data_node(
        cls,
        id: str,
        db_name: str,
        db_engine: str,
        read_query: str,
        write_query_builder: Callable,
        append_query_builder: Optional[Callable] = None,
        db_username: Optional[str] = None,
        db_password: Optional[str] = None,
        db_host: Optional[str] = None,
        db_port: Optional[int] = None,
        db_driver: Optional[str] = None,
        sqlite_folder_path: Optional[str] = None,
        sqlite_file_extension: Optional[str] = None,
        db_extra_args: Optional[Dict[str, Any]] = None,
        exposed_type: Optional[str] = None,
        scope: Optional[Scope] = None,
        validity_period: Optional[timedelta] = None,
        **properties,
    ) -> "DataNodeConfig":
        """Configure a new SQL data node configuration.

        Parameters:
            id (str): The unique identifier of the new SQL data node configuration.
            db_name (str): The database name, or the name of the SQLite database file.
            db_engine (str): The database engine. Possible values are *"sqlite"*, *"mssql"*, *"mysql"*,
                or *"postgresql"*.
            read_query (str): The SQL query string used to read the data from the database.
            write_query_builder (Callable): A callback function that takes the data as an input parameter
                and returns a list of SQL queries to be executed when writing data to the data node.
            append_query_builder (Optional[Callable]): A callback function that takes the data as an input parameter
                and returns a list of SQL queries to be executed when appending data to the data node.
            db_username (Optional[str]): The database username. Required by the *"mssql"*, *"mysql"*, and
                *"postgresql"* engines.
            db_password (Optional[str]): The database password. Required by the *"mssql"*, *"mysql"*, and
                *"postgresql"* engines.
            db_host (Optional[str]): The database host.<br/>
                The default value is "localhost".
            db_port (Optional[int]): The database port.<br/>
                The default value is 1433.
            db_driver (Optional[str]): The database driver.
            sqlite_folder_path (Optional[str]): The path to the folder that contains SQLite file.<br/>
                The default value is the current working folder.
            sqlite_file_extension (Optional[str]): The file extension of the SQLite file.<br/>
                The default value is ".db".
            db_extra_args (Optional[dict[str, any]]): A dictionary of additional arguments to be passed
                into database connection string.
            exposed_type (Optional[str]): The exposed type of the data read from SQL query.<br/>
                The default value is "pandas".
            scope (Optional[Scope^]): The scope of the SQL data node configuration.<br/>
                The default value is `Scope.SCENARIO`.
            validity_period (Optional[timedelta]): The duration since the last edit date for which the data node can be
                considered up-to-date. Once the validity period has passed, the data node is considered stale and
                relevant tasks will run even if they are skippable (see the Task configuration
                [page](../../../../../../userman/scenario_features/task-orchestration/scenario-config.md#from-task-configurations)
                for more details).
                If *validity_period* is set to None, the data node is always up-to-date.
            **properties (dict[str, any]): A keyworded variable length list of additional arguments.

        Returns:
            The new SQL data node configuration.
        """  # noqa: E501

    @classmethod
    def configure_mongo_collection_data_node(
        cls,
        id: str,
        db_name: str,
        collection_name: str,
        custom_document: Optional[Any] = None,
        db_username: Optional[str] = None,
        db_password: Optional[str] = None,
        db_host: Optional[str] = None,
        db_port: Optional[int] = None,
        db_driver: Optional[str] = None,
        db_extra_args: Optional[Dict[str, Any]] = None,
        scope: Optional[Scope] = None,
        validity_period: Optional[timedelta] = None,
        **properties,
    ) -> "DataNodeConfig":
        """Configure a new Mongo collection data node configuration.

        Parameters:
            id (str): The unique identifier of the new Mongo collection data node configuration.
            db_name (str): The database name.
            collection_name (str): The collection in the database to read from and to write the data to.
            custom_document (Optional[any]): The custom document class to store, encode, and decode data
                when reading and writing to a Mongo collection. The custom_document can have an optional
                *decode()* method to decode data in the Mongo collection to a custom object, and an
                optional *encode()*) method to encode the object's properties to the Mongo collection
                when writing.
            db_username (Optional[str]): The database username.
            db_password (Optional[str]): The database password.
            db_host (Optional[str]): The database host.<br/>
                The default value is "localhost".
            db_port (Optional[int]): The database port.<br/>
                The default value is 27017.
            db_driver (Optional[str]): The database driver.
            db_extra_args (Optional[dict[str, any]]): A dictionary of additional arguments to be passed
                into database connection string.
            scope (Optional[Scope^]): The scope of the Mongo collection data node configuration.<br/>
                The default value is `Scope.SCENARIO`.
            validity_period (Optional[timedelta]): The duration since the last edit date for which the data node can be
                considered up-to-date. Once the validity period has passed, the data node is considered stale and
                relevant tasks will run even if they are skippable (see the Task configuration
                [page](../../../../../../userman/scenario_features/task-orchestration/scenario-config.md#from-task-configurations)
                for more details).
                If *validity_period* is set to None, the data node is always up-to-date.
            **properties (dict[str, any]): A keyworded variable length list of additional arguments.

        Returns:
            The new Mongo collection data node configuration.
        """  # noqa: E501

    @classmethod
    def configure_s3_object_data_node(
        cls,
        id: str,
        aws_access_key: str,
        aws_secret_access_key: str,
        aws_s3_bucket_name: str,
        aws_s3_object_key: str,
        aws_region: Optional[str] = None,
        aws_s3_object_parameters: Optional[Dict[str, Any]] = None,
        scope: Optional[Scope] = None,
        validity_period: Optional[timedelta] = None,
        **properties,
    ) -> "DataNodeConfig":
        """Configure a new S3 object data node configuration.

        Parameters:
            id (str): The unique identifier of the new S3 Object data node configuration.
            aws_access_key (str): Amazon Web Services ID for to identify account.
            aws_secret_access_key (str): Amazon Web Services access key to authenticate programmatic requests.
            aws_s3_bucket_name (str): The bucket in S3 to read from and to write the data to.
            aws_region (Optional[str]): Self-contained geographic area where Amazon Web Services (AWS)
                infrastructure is located.
            aws_s3_object_parameters (Optional[dict[str, any]]): A dictionary of additional arguments to be passed
                into AWS S3 bucket access string.
            scope (Optional[Scope^]): The scope of the S3 Object data node configuration.<br/>
                The default value is `Scope.SCENARIO`.
            validity_period (Optional[timedelta]): The duration since the last edit date for which the data node can be
                considered up-to-date. Once the validity period has passed, the data node is considered stale and
                relevant tasks will run even if they are skippable (see the Task configuration
                [page](../../../../../../userman/scenario_features/task-orchestration/scenario-config.md#from-task-configurations)
                for more details).
                If *validity_period* is set to None, the data node is always up-to-date.
            **properties (dict[str, any]): A keyworded variable length list of additional arguments.

        Returns:
            The new S3 object data node configuration.
        """  # noqa: E501

    @staticmethod
    def configure_task(
        id: str,
        function: Optional[Callable],
        input: Optional[Union[DataNodeConfig, List[DataNodeConfig]]] = None,
        output: Optional[Union[DataNodeConfig, List[DataNodeConfig]]] = None,
        skippable: bool = False,
        **properties,
    ) -> "TaskConfig":
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
                been made on inputs.<br/>
                The default value is False.
            **properties (dict[str, any]): A keyworded variable length list of additional arguments.

        Returns:
            The new task configuration.
        """

    @staticmethod
    def set_default_task_configuration(
        function: Optional[Callable],
        input: Optional[Union[DataNodeConfig, List[DataNodeConfig]]] = None,
        output: Optional[Union[DataNodeConfig, List[DataNodeConfig]]] = None,
        skippable: bool = False,
        **properties,
    ) -> "TaskConfig":
        """Set the default values for task configurations.

        This function creates the *default task configuration* object,
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
                been made on inputs.<br/>
                The default value is False.
            **properties (dict[str, any]): A keyworded variable length list of additional
                arguments.

        Returns:
            The default task configuration.
        """

    @staticmethod
    def configure_job_executions(
        mode: Optional[str] = None, max_nb_of_workers: Optional[Union[int, str]] = None, **properties
    ) -> "JobConfig":
        """Configure job execution.

        Parameters:
            mode (Optional[str]): The job execution mode.
                Possible values are: *"standalone"* or *"development"*.
            max_nb_of_workers (Optional[int, str]): Parameter used only in *"standalone"* mode.
                This indicates the maximum number of jobs able to run in parallel.<br/>
                The default value is 2.<br/>
                A string can be provided to dynamically set the value using an environment
                variable. The string must follow the pattern: `ENV[&lt;env_var&gt;]` where
                `&lt;env_var&gt;` is the name of an environment variable.
            **properties (dict[str, any]): A keyworded variable length list of additional arguments.

        Returns:
            The new job execution configuration.
        """

    @staticmethod
    def configure_core(
        root_folder: Optional[str] = None,
        storage_folder: Optional[str] = None,
        taipy_storage_folder: Optional[str] = None,
        repository_type: Optional[str] = None,
        repository_properties: Optional[Dict[str, Union[str, int]]] = None,
        read_entity_retry: Optional[int] = None,
        mode: Optional[str] = None,
        version_number: Optional[str] = None,
        force: Optional[bool] = None,
        **properties,
    ) -> "CoreSection":
        """Configure the Orchestrator service.

        Parameters:
            root_folder (Optional[str]): Path of the base folder for the taipy application.
                The default value is "./taipy/"
            storage_folder (str): Folder name used to store user data. The default value is "user_data/". It is used in
                conjunction with the *root_folder* attribute. That means the storage path is
                <root_folder><storage_folder> (The default path is "./taipy/user_data/").
            taipy_storage_folder (str): Folder name used to store Taipy data. The default value is ".taipy/". It is
                used in conjunction with the *root_folder* attribute. That means the storage path is
                <root_folder><storage_folder> (The default path is "./taipy/.taipy/").
            repository_type (Optional[str]): The type of the repository to be used to store Taipy data.
                The default value is "filesystem".
            repository_properties (Optional[Dict[str, Union[str, int]]]): A dictionary of additional properties
                to be used by the repository.
            read_entity_retry (Optional[int]): Number of retries to read an entity from the repository
                before return failure. The default value is 3.
            mode (Optional[str]): Indicates the mode of the version management system.
                Possible values are *"development"* or *"experiment"*. On Enterprise edition of Taipy,
                *production* mode is also available. Please refer to the
                [Versioning management](../../../../../../userman/advanced_features/versioning/index.md)
                documentation page for more details.
            version_number (Optional[str]): The string identifier of the version.
                 In development mode, the version number is ignored.
            force (Optional[bool]): If True, Taipy will override a version even if the configuration
                has changed and run the application.
            **properties (Dict[str, Any]): A keyworded variable length list of additional arguments configure the
                behavior of the `Orchestrator^` service.

        Returns:
            The Core configuration.
        """
