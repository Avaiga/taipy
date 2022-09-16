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
from abc import abstractmethod
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import pandas as pd
from sqlalchemy import create_engine, text

from taipy.config.common.scope import Scope

from ..common.alias import DataNodeId, JobId
from ..exceptions.exceptions import InvalidExposedType, MissingRequiredProperty, UnknownDatabaseEngine
from .data_node import DataNode


class AbstractSQLDataNode(DataNode):
    """Abstract base class for data node implementations (SQLDataNode and SQLTableDataNode) that use SQL."""

    __STORAGE_TYPE = None
    __EXPOSED_TYPE_NUMPY = "numpy"
    __EXPOSED_TYPE_PANDAS = "pandas"
    __VALID_STRING_EXPOSED_TYPES = [__EXPOSED_TYPE_PANDAS, __EXPOSED_TYPE_NUMPY]
    __EXPOSED_TYPE_PROPERTY = "exposed_type"
    __DB_EXTRA_ARGS_KEY = "db_extra_args"
    __ENGINE_MSSQL = "mssql"
    __ENGINE_SQLITE = "sqlite"

    _ENGINE_REQUIRED_PROPERTIES: Dict[str, List[str]] = {
        __ENGINE_MSSQL: ["db_username", "db_password", "db_name"],
        __ENGINE_SQLITE: ["db_name", "path"],
    }

    def __init__(
        self,
        config_id: str,
        scope: Scope,
        id: Optional[DataNodeId] = None,
        name: Optional[str] = None,
        parent_id: Optional[str] = None,
        last_edit_date: Optional[datetime] = None,
        job_ids: List[JobId] = None,
        cacheable: bool = False,
        validity_period: Optional[timedelta] = None,
        edit_in_progress: bool = False,
        properties: Dict = None,
    ):
        if properties is None:
            properties = {}

        if self.__EXPOSED_TYPE_PROPERTY not in properties.keys():
            properties[self.__EXPOSED_TYPE_PROPERTY] = self.__EXPOSED_TYPE_PANDAS
        self._check_exposed_type(properties[self.__EXPOSED_TYPE_PROPERTY])

        super().__init__(
            config_id,
            scope,
            id,
            name,
            parent_id,
            last_edit_date,
            job_ids,
            cacheable,
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

    def _check_required_properties(self, properties: Dict):
        db_engine = properties.get("db_engine")
        if not db_engine:
            raise MissingRequiredProperty("db_engine is required.")
        if db_engine not in self._ENGINE_REQUIRED_PROPERTIES.keys():
            raise UnknownDatabaseEngine(f"Unknown engine: {db_engine}")
        required = self._ENGINE_REQUIRED_PROPERTIES[db_engine]

        if missing := set(required) - set(properties.keys()):
            raise MissingRequiredProperty(
                f"The following properties " f"{', '.join(x for x in missing)} were not informed and are required"
            )

    def _check_exposed_type(self, exposed_type):
        if isinstance(exposed_type, str) and exposed_type not in self.__VALID_STRING_EXPOSED_TYPES:
            raise InvalidExposedType(
                f"Invalid string exposed type {exposed_type}. Supported values are {', '.join(self.__VALID_STRING_EXPOSED_TYPES)}"
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
        if self.properties[self.__EXPOSED_TYPE_PROPERTY] == self.__EXPOSED_TYPE_PANDAS:
            return self._read_as_pandas_dataframe()
        if self.properties[self.__EXPOSED_TYPE_PROPERTY] == self.__EXPOSED_TYPE_NUMPY:
            return self._read_as_numpy()
        return self._read_as()

    def _read_as(self):
        custom_class = self.properties[self.__EXPOSED_TYPE_PROPERTY]
        with self.__engine().connect() as connection:
            query_result = connection.execute(text(self._get_read_query()))
        return list(map(lambda row: custom_class(**row), query_result))

    def _read_as_numpy(self):
        return self._read_as_pandas_dataframe().to_numpy()

    def _read_as_pandas_dataframe(self, columns: Optional[List[str]] = None):
        if columns:
            return pd.read_sql_query(self._get_read_query(), con=self.__engine())[columns]
        return pd.read_sql_query(self._get_read_query(), con=self.__engine())

    @abstractmethod
    def _get_read_query(self):
        raise NotImplementedError

    @abstractmethod
    def _do_write(self, data, engine, connection) -> None:
        raise NotImplementedError

    def _write(self, data) -> None:
        """Check data against a collection of types to handle insertion on the database."""
        engine = self.__engine()
        with engine.connect() as connection:
            with connection.begin() as transaction:
                try:
                    self._do_write(data, engine, connection)
                except:
                    transaction.rollback()
                    raise
                else:
                    transaction.commit()
