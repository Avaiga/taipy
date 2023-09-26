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
from typing import Any, Dict, List, Optional, Set, Tuple, Union

import modin.pandas as modin_pd
import numpy as np
import pandas as pd
from sqlalchemy import MetaData, Table

from taipy.config.common.scope import Scope

from .._version._version_manager_factory import _VersionManagerFactory
from ..exceptions.exceptions import MissingRequiredProperty
from ._abstract_sql import _AbstractSQLDataNode
from .data_node_id import DataNodeId, Edit


class SQLTableDataNode(_AbstractSQLDataNode):
    """Data Node stored in a SQL table.

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
            _properties_ parameter must at least contain an entry for _"db_name"_, _"db_engine"_, _"table_name"_:

            - _"db_name"_ `(str)`: The database name, or the name of the SQLite database file.
            - _"db_engine"_ `(str)`: The database engine. For now, the accepted values are _"sqlite"_, _"mssql"_,
                _"mysql"_, or _"postgresql"_.
            - _"table_name"_ `(str)`: The name of the SQL table.
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

    __STORAGE_TYPE = "sql_table"
    __TABLE_KEY = "table_name"

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
        if properties.get(self.__TABLE_KEY) is None:
            raise MissingRequiredProperty(f"Property {self.__TABLE_KEY} is not informed and is required")
        super().__init__(
            config_id,
            scope,
            id=id,
            name=name,
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
        return cls.__STORAGE_TYPE

    def _get_read_query(self):
        return f"SELECT * FROM {self.properties[self.__TABLE_KEY]}"

    def _do_write(self, data, engine, connection) -> None:
        table = self._create_table(engine)
        if isinstance(data, (modin_pd.DataFrame, pd.DataFrame)):
            self._insert_dataframe(data, table, connection)
        else:
            if isinstance(data, np.ndarray):
                data = data.tolist()
            if not isinstance(data, list):
                data = [data]
            if len(data) == 0:
                self._delete_all_rows(table, connection)
            else:
                if isinstance(data[0], (tuple, list)):
                    self._insert_tuples(data, table, connection)
                elif isinstance(data[0], dict):
                    self._insert_dicts(data, table, connection)
                # If data is a primitive type, it will be inserted as a tuple of one element.
                else:
                    self._insert_tuples([(x,) for x in data], table, connection)

    def _create_table(self, engine) -> Table:
        return Table(
            self.table,
            MetaData(),
            autoload=True,
            autoload_with=engine,
        )

    @staticmethod
    def _insert_dicts(data: List[Dict], table: Any, connection: Any) -> None:
        """
        This method will insert the data contained in a list of dictionaries into a table. The query itself is handled
        by SQLAlchemy, so it's only needed to pass the correct data type.
        """
        connection.execute(table.delete())
        connection.execute(table.insert(), data)

    @staticmethod
    def _insert_dataframe(df: Union[modin_pd.DataFrame, pd.DataFrame], table: Any, connection: Any) -> None:
        """
        :param data: a pandas dataframe
        :param table: a SQLAlchemy object that represents a table
        :param connection: a SQLAlchemy connection to write the data
        """
        SQLTableDataNode._insert_dicts(df.to_dict(orient="records"), table, connection)

    @staticmethod
    def _delete_all_rows(table, connection):
        connection.execute(table.delete())

    @staticmethod
    def _insert_tuples(data: List[Union[Tuple, List]], table: Any, connection: Any) -> None:
        """
        This method will look up the length of the first object of the list and build the insert through
        creation of a string of '?' equivalent to the length of the element. The '?' character is used as
        placeholder for a tuple of same size.
        """
        connection.execute(table.delete())
        markers = ",".join("?" * len(data[0]))
        ins = "INSERT INTO {tablename} VALUES ({markers})"
        ins = ins.format(tablename=table.name, markers=markers)
        connection.execute(ins, data)
