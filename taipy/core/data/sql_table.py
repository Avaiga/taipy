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
from typing import Any, Dict, List, Optional, Set, Union

import pandas as pd
from sqlalchemy import MetaData, Table

from taipy.common.config.common.scope import Scope

from .._version._version_manager_factory import _VersionManagerFactory
from ..exceptions.exceptions import MissingRequiredProperty
from ._abstract_sql import _AbstractSQLDataNode
from .data_node_id import DataNodeId, Edit


class SQLTableDataNode(_AbstractSQLDataNode):
    """Data Node stored in a SQL table.
    The *properties* attribute must contain the following mandatory entries:

    - *has_header* (`bool`): If True, indicates that the SQL query has a header.
    - *exposed_type* (`str`): The exposed type of the data read from SQL query. The default value is `pandas`.
    - *db_name* (`str`): The database name, or the name of the SQLite database file.
    - *db_engine* (`str`): The database engine. Possible values are *sqlite*, *mssql*,
        *mysql*, or *postgresql*.
    - *table_name* (`str`): The name of the SQL table.
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

    __STORAGE_TYPE = "sql_table"
    __TABLE_KEY = "table_name"

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
        if properties.get(self.__TABLE_KEY) is None:
            raise MissingRequiredProperty(f"Property {self.__TABLE_KEY} is not informed and is required.")
        super().__init__(
            config_id,
            scope,
            id=id,
            owner_id=owner_id,
            parent_ids=parent_ids,
            last_edit_date=last_edit_date,
            edits=edits,
            version=version or _VersionManagerFactory._build_manager()._get_latest_version(),
            validity_period=validity_period,
            edit_in_progress=edit_in_progress,
            editor_id=editor_id,
            editor_expiration_date=editor_expiration_date,
            properties=properties,
        )
        self._TAIPY_PROPERTIES.update({self.__TABLE_KEY})

    @classmethod
    def storage_type(cls) -> str:
        """Return the storage type of the data node: `sql_table`."""
        return cls.__STORAGE_TYPE

    def _get_base_read_query(self) -> str:
        return f"SELECT * FROM {self.properties[self.__TABLE_KEY]}"

    def _do_append(self, data, engine, connection) -> None:
        self.__insert_data(data, engine, connection)

    def _do_write(self, data, engine, connection) -> None:
        self.__insert_data(data, engine, connection, delete_table=True)

    def __insert_data(self, data, engine, connection, delete_table: bool = False) -> None:
        table = self._create_table(engine)
        self._insert_dataframe(
            self._convert_data_to_dataframe(self.properties[self._EXPOSED_TYPE_PROPERTY], data),
            table,
            connection,
            delete_table,
        )

    def _create_table(self, engine) -> Table:
        return Table(
            self.properties[self.__TABLE_KEY],
            MetaData(),
            autoload_with=engine,
        )

    @classmethod
    def _insert_dicts(cls, data: List[Dict], table: Any, connection: Any, delete_table: bool) -> None:
        """
        This method will insert the data contained in a list of dictionaries into a table. The query itself is handled
        by SQLAlchemy, so it's only needed to pass the correct data type.
        """
        cls.__delete_all_rows(table, connection, delete_table)
        connection.execute(table.insert(), data)

    @classmethod
    def _insert_dataframe(
        cls, df: Union[pd.DataFrame, pd.Series], table: Any, connection: Any, delete_table: bool
    ) -> None:
        if isinstance(df, pd.Series):
            data = [df.to_dict()]
        elif isinstance(df, pd.DataFrame):
            data = df.to_dict(orient="records")
        cls._insert_dicts(data, table, connection, delete_table)

    @classmethod
    def __delete_all_rows(cls, table: Any, connection: Any, delete_table: bool) -> None:
        if delete_table:
            connection.execute(table.delete())
