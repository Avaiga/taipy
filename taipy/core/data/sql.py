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

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set

from sqlalchemy import text

from taipy.common.config.common.scope import Scope

from .._version._version_manager_factory import _VersionManagerFactory
from ..exceptions.exceptions import MissingAppendQueryBuilder, MissingRequiredProperty
from ._abstract_sql import _AbstractSQLDataNode
from .data_node_id import DataNodeId, Edit


class SQLDataNode(_AbstractSQLDataNode):
    """Data Node stored in a SQL database.

    The *properties* attribute must contain the following mandatory entries:

    - *has_header* (`bool`): If True, indicates that the SQL query has a header.
    - *exposed_type* (`str`): The exposed type of the data read from SQL query. The default value is `pandas`.
    - *db_name* (`str`): The database name, or the name of the SQLite database file.
    - *db_engine* (`str`): The database engine. Possible values are *sqlite*, *mssql*,
        *mysql*, or *postgresql*.
    - *read_query* (`str`): The SQL query string used to read the data from the database.
    - *write_query_builder* `(Callable)`: A callback function that takes the data as an input
        parameter and returns a list of SQL queries to be executed when writing data to the data
        node.
    - *append_query_builder* (`Callable`): A callback function that takes the data as an input
        parameter and returns a list of SQL queries to be executed when appending data to the
        data node.
    - *db_username* (`str`): The database username.
    - *db_password* (`str`): The database password.
    - *db_host* (`str`): The database host. The default value is *localhost*.
    - *db_port* (`int`): The database port. The default value is 1433.
    - *db_driver* (`str`): The database driver.

    The *properties* attribute can also contain the following optional entries:

    - *sqlite_folder_path* (str): The path to the folder that contains SQLite file. The default value
        is the current working folder.
    - *sqlite_file_extension* (str): The filename extension of the SQLite file. The default value is ".db".
    - *db_extra_args* (`Dict[str, Any]`): A dictionary of additional arguments to be passed into database
        connection string.
    """

    __STORAGE_TYPE = "sql"
    __READ_QUERY_KEY = "read_query"
    _WRITE_QUERY_BUILDER_KEY = "write_query_builder"
    _APPEND_QUERY_BUILDER_KEY = "append_query_builder"

    def __init__(
        self,
        config_id: str,
        scope: Scope,
        id: Optional[DataNodeId] = None,
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
    ) -> None:
        if properties is None:
            properties = {}
        if properties.get(self.__READ_QUERY_KEY) is None:
            raise MissingRequiredProperty(f"Property {self.__READ_QUERY_KEY} is not informed and is required.")
        if properties.get(self._WRITE_QUERY_BUILDER_KEY) is None:
            raise MissingRequiredProperty(f"Property {self._WRITE_QUERY_BUILDER_KEY} is not informed and is required.")

        super().__init__(
            config_id,
            scope,
            id,
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
                self._APPEND_QUERY_BUILDER_KEY,
            }
        )

    @classmethod
    def storage_type(cls) -> str:
        """Return the storage type of the data node: "sql"."""
        return cls.__STORAGE_TYPE

    def _get_base_read_query(self) -> str:
        return self.properties.get(self.__READ_QUERY_KEY)

    def _do_append(self, data, engine, connection) -> None:
        append_query_builder_fct = self.properties.get(self._APPEND_QUERY_BUILDER_KEY)
        if not append_query_builder_fct:
            raise MissingAppendQueryBuilder

        queries = append_query_builder_fct(data)
        self.__execute_queries(queries, connection)

    def _do_write(self, data, engine, connection) -> None:
        queries = self.properties.get(self._WRITE_QUERY_BUILDER_KEY)(data)
        self.__execute_queries(queries, connection)

    def __execute_queries(self, queries, connection) -> None:
        if not isinstance(queries, List):
            queries = [queries]
        for query in queries:
            if isinstance(query, str):
                connection.execute(text(query))
            else:
                statement = query[0]
                parameters = query[1]
                connection.execute(text(statement), parameters)
