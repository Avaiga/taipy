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

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set

from taipy.config.common.scope import Scope

from .._version._version_manager_factory import _VersionManagerFactory
from ..exceptions.exceptions import MissingRequiredProperty
from ._abstract_sql import _AbstractSQLDataNode
from .data_node_id import DataNodeId, Edit


class SQLDataNode(_AbstractSQLDataNode):
    """Data Node stored in a SQL database.

    Attributes:
        config_id (str): Identifier of the data node configuration. It must be a valid Python
            identifier.
        scope (Scope^): The scope of this data node.
        id (str): The unique identifier of this data node.
        name (str): A user-readable name of this data node.
        owner_id (str): The identifier of the owner (sequence_id, scenario_id, cycle_id) or
            None.
        parent_ids (Optional[Set[str]]): The identifiers of the parent tasks or `None`.
        last_edit_date (datetime): The date and time of the last modification.
        edits (List[Edit^]): The ordered list of edits for that job.
        version (str): The string indicates the application version of the data node to instantiate. If not provided,
            the current version is used.
        validity_period (Optional[timedelta]): The duration implemented as a timedelta since the last edit date for
            which the data node can be considered up-to-date. Once the validity period has passed, the data node is
            considered stale and relevant tasks will run even if they are skippable (see the
            [Task management page](../core/entities/task-mgt.md) for more details).
            If _validity_period_ is set to `None`, the data node is always up-to-date.
        edit_in_progress (bool): True if a task computing the data node has been submitted
            and not completed yet. False otherwise.
        editor_id (Optional[str]): The identifier of the user who is currently editing the data node.
        editor_expiration_date (Optional[datetime]): The expiration date of the editor lock.
        properties (dict[str, Any]): A dictionary of additional properties. Note that the
            _properties_ parameter must at least contain an entry for _"db_name"_, _"db_engine"_, _"read_query"_,
            and _"write_query_builder"_:

            - _"db_name"_ `(str)`: The database name, or the name of the SQLite database file.
            - _"db_engine"_ `(str)`: The database engine. Possible values are _"sqlite"_, _"mssql"_, _"mysql"_, or
                _"postgresql"_.
            - _"read_query"_ `(str)`: The SQL query string used to read the data from the database.
            - _"write_query_builder"_ `(Callable)`: A callback function that takes the data as an input parameter and
                returns a list of SQL queries.
            - _"db_username"_ `(str)`: The database username.
            - _"db_password"_ `(str)`: The database password.
            - _"db_host"_ `(str)`: The database host. The default value is _"localhost"_.
            - _"db_port"_ `(int)`: The database port. The default value is 1433.
            - _"db_driver"_ `(str)`: The database driver.
            - _"sqlite_folder_path"_ (str): The path to the folder that contains SQLite file. The default value
                is the current working folder.
            - _"sqlite_file_extension"_ (str): The filename extension of the SQLite file. The default value is ".db".
            - _"db_extra_args"_ `(Dict[str, Any])`: A dictionary of additional arguments to be passed into database
                connection string.
            - _"exposed_type"_: The exposed type of the data read from SQL query. The default value is `pandas`.
    """

    __STORAGE_TYPE = "sql"
    __READ_QUERY_KEY = "read_query"
    _WRITE_QUERY_BUILDER_KEY = "write_query_builder"

    def __init__(
        self,
        config_id: str,
        scope: Scope,
        id: Optional[DataNodeId] = None,
        name: Optional[str] = None,
        owner_id: Optional[str] = None,
        parent_ids: Optional[Set[str]] = None,
        last_edit_date: Optional[datetime] = None,
        edits: Optional[List[Edit]] = None,
        version: Optional[str] = None,
        validity_period: Optional[timedelta] = None,
        edit_in_progress: bool = False,
        editor_id: Optional[str] = None,
        editor_expiration_date: Optional[datetime] = None,
        properties: Optional[Dict] = None,
    ):
        if properties is None:
            properties = {}
        if properties.get(self.__READ_QUERY_KEY) is None:
            raise MissingRequiredProperty(f"Property {self.__READ_QUERY_KEY} is not informed and is required")
        if properties.get(self._WRITE_QUERY_BUILDER_KEY) is None:
            raise MissingRequiredProperty(f"Property {self._WRITE_QUERY_BUILDER_KEY} is not informed and is required")

        super().__init__(
            config_id,
            scope,
            id,
            name,
            owner_id,
            parent_ids,
            last_edit_date,
            edits,
            version or _VersionManagerFactory._build_manager()._get_latest_version(),
            validity_period,
            edit_in_progress,
            editor_id,
            editor_expiration_date,
            properties=properties,
        )

        self._TAIPY_PROPERTIES.update(
            {
                self.__READ_QUERY_KEY,
                self._WRITE_QUERY_BUILDER_KEY,
            }
        )

    @classmethod
    def storage_type(cls) -> str:
        return cls.__STORAGE_TYPE

    def _get_read_query(self):
        return self.properties.get(self.__READ_QUERY_KEY)

    def _do_write(self, data, engine, connection) -> None:
        queries = self.properties.get(self._WRITE_QUERY_BUILDER_KEY)(data)
        if not isinstance(queries, list):
            queries = [queries]
        for query in queries:
            if isinstance(query, str):
                connection.execute(query)
            else:
                connection.execute(*query)
