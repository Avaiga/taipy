# Copyright 2022 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import os
import re
import urllib.parse
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
from sqlalchemy import MetaData, Table, create_engine, text

from taipy.config.common.scope import Scope
from ..common.alias import DataNodeId, JobId
from ..exceptions.exceptions import MissingRequiredProperty, UnknownDatabaseEngine
from .data_node import DataNode


class SQLDataNode(DataNode):
    """Data Node stored in a SQL database.

    Attributes:
        config_id (str): Identifier of the data node configuration. It must be a valid Python
            identifier.
        scope (Scope^): The scope of this data node.
        id (str): The unique identifier of this data node.
        name (str): A user-readable name of this data node.
        parent_id (str): The identifier of the parent (pipeline_id, scenario_id, cycle_id) or
            None.
        last_edit_date (datetime): The date and time of the last modification.
        job_ids (List[str]): The ordered list of jobs that have written this data node.
        validity_period (Optional[timedelta]): The validity period of a cacheable data node.
            Implemented as a timedelta. If _validity_period_ is set to None, the data_node is
            always up-to-date.
        edit_in_progress (bool): True if a task computing the data node has been submitted
            and not completed yet. False otherwise.
        properties (dict[str, Any]): A dictionary of additional properties. Note that the
            _properties_ parameter must at least contain an entry for _"db_username"_,
            _"db_password"_, _"db_name"_, _"db_engine"_, _"read_query"_, and _"write_table"_.
            For now, the accepted values for the _"db_engine"_ property are _"mssql"_ and
            _"sqlite"_.
    """

    __STORAGE_TYPE = "sql"
    __EXPOSED_TYPE_NUMPY = "numpy"
    __EXPOSED_TYPE_PROPERTY = "exposed_type"
    __DB_EXTRA_ARGS_KEY = "db_extra_args"
    _REQUIRED_PROPERTIES: List[str] = [
        "db_username",
        "db_password",
        "db_name",
        "db_engine",
        "read_query",
        "write_table",
    ]

    def __init__(
        self,
        config_id: str,
        scope: Scope,
        id: Optional[DataNodeId] = None,
        name: Optional[str] = None,
        parent_id: Optional[str] = None,
        last_edit_date: Optional[datetime] = None,
        job_ids: List[JobId] = None,
        validity_period: Optional[timedelta] = None,
        edit_in_progress: bool = False,
        properties: Dict = None,
    ):
        if properties is None:
            properties = {}
        required = (
            self._REQUIRED_PROPERTIES
            if properties.get("db_engine") != "sqlite"
            else ["db_name", "read_query", "write_table"]
        )
        if missing := set(required) - set(properties.keys()):
            raise MissingRequiredProperty(
                f"The following properties " f"{', '.join(x for x in missing)} were not informed and are required"
            )

        super().__init__(
            config_id,
            scope,
            id,
            name,
            parent_id,
            last_edit_date,
            job_ids,
            validity_period,
            edit_in_progress,
            **properties,
        )
        if not self._last_edit_date:
            self.unlock_edit()

    def __engine(self):
        return self.__create_engine(
            self.properties.get("db_engine"),
            self.properties.get("db_username"),
            self.properties.get("db_host", "localhost"),
            self.properties.get("db_password"),
            self.properties.get("db_name"),
            self.properties.get("db_port", 1433),
            self.properties.get("db_driver", "ODBC Driver 17 for SQL Server"),
            self.properties.get(self.__DB_EXTRA_ARGS_KEY, {}),
            self.properties.get("path", ""),
        )

    @staticmethod
    def __build_conn_string(
        engine, username, host, password, database, port, driver, extra_args: Dict[str, str], path
    ) -> str:
        # TODO: Add support to other SQL engines, the engine value should be checked.
        if engine == "mssql":
            username = urllib.parse.quote_plus(username)
            password = urllib.parse.quote_plus(password)
            database = urllib.parse.quote_plus(database)

            extra_args = {**extra_args, "driver": driver}
            for k, v in extra_args.items():
                extra_args[k] = re.sub(r"\s+", "+", v)
            extra_args_str = "&".join(f"{k}={str(v)}" for k, v in extra_args.items())

            return f"mssql+pyodbc://{username}:{password}@{host}:{port}/{database}?{extra_args_str}"
        elif engine == "sqlite":
            return os.path.join("sqlite:///", path, f"{database}.sqlite3")
        raise UnknownDatabaseEngine(f"Unknown engine: {engine}")

    def __create_engine(self, engine, username, host, password, database, port, driver, extra_args, path):
        conn_str = self.__build_conn_string(engine, username, host, password, database, port, driver, extra_args, path)
        return create_engine(conn_str)

    @classmethod
    def storage_type(cls) -> str:
        return cls.__STORAGE_TYPE

    def _read(self):
        if self.__EXPOSED_TYPE_PROPERTY in self.properties:
            if self.properties[self.__EXPOSED_TYPE_PROPERTY] == self.__EXPOSED_TYPE_NUMPY:
                return self._read_as_numpy()
            return self._read_as(self.properties[self.__EXPOSED_TYPE_PROPERTY])
        return self._read_as_pandas_dataframe()

    def _read_as(self, query, custom_class):
        with self.__engine().connect() as connection:
            query_result = connection.execute(text(query))
        return list(map(lambda row: custom_class(**row), query_result))

    def _read_as_numpy(self):
        return self._read_as_pandas_dataframe().to_numpy()

    def _read_as_pandas_dataframe(self, columns: Optional[List[str]] = None):
        if columns:
            return pd.read_sql_query(self.read_query, con=self.__engine())[columns]
        return pd.read_sql_query(self.read_query, con=self.__engine())

    def _create_table(self, engine) -> Table:
        return Table(
            self.write_table,
            MetaData(),
            autoload=True,
            autoload_with=engine,
        )

    def _write(self, data) -> None:
        """Check data against a collection of types to handle insertion on the database."""

        engine = self.__engine()

        if isinstance(data, pd.DataFrame):
            data = data.to_dict(orient="records")
        elif isinstance(data, np.ndarray):
            data = data.tolist()
        if not isinstance(data, list):
            data = [data]
        if len(data) == 0:
            return
        with engine.connect() as connection:
            table = self._create_table(engine)
            if isinstance(data[0], (tuple, list)):
                self._insert_tuples(data, table, connection)
            elif isinstance(data[0], dict):
                self._insert_dicts(data, table, connection)
            # If data is a primitive type, it will be inserted as a tuple of one element.
            else:
                self._insert_tuples([(x,) for x in data], table, connection)

    @staticmethod
    def _insert_tuples(data: List[Union[Tuple, List]], write_table: Any, connection: Any) -> None:
        """
        :param data: a list of tuples or lists
        :param write_table: a SQLAlchemy object that represents a table
        :param connection: a SQLAlchemy connection to write the data

        This method will lookup the length of the first object of the list and build the insert through
        creation of a string of '?' equivalent to the length of the element. The '?' character is used as
        placeholder for a tuple of same size.
        """
        with connection.begin() as transaction:
            try:
                markers = ",".join("?" * len(data[0]))
                ins = "INSERT INTO {tablename} VALUES ({markers})"
                ins = ins.format(tablename=write_table.name, markers=markers)
                connection.execute(ins, data)
            except:
                transaction.rollback()
                raise
            else:
                transaction.commit()

    @staticmethod
    def _insert_dicts(data: List[Dict], write_table: Any, connection: Any) -> None:
        """
        :param data: a list of dictionaries
        :param write_table: a SQLAlchemy object that represents a table
        :param connection: a SQLAlchemy connection to write the data

        This method will insert the data contained in a list of dictionaries into a table. The query itself is handled
        by SQLAlchemy, so it's only needed to pass the correctly data type.
        """
        with connection.begin() as transaction:
            try:
                connection.execute(write_table.insert(), data)
            except:
                transaction.rollback()
                raise
            else:
                transaction.commit()
