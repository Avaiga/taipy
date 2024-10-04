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

import os
import re
import urllib.parse
from abc import abstractmethod
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple, Union

import numpy as np
import pandas as pd
from sqlalchemy import create_engine, text

from taipy.common.config.common.scope import Scope

from .._version._version_manager_factory import _VersionManagerFactory
from ..data.operator import JoinOperator, Operator
from ..exceptions.exceptions import MissingRequiredProperty, UnknownDatabaseEngine
from ._tabular_datanode_mixin import _TabularDataNodeMixin
from .data_node import DataNode
from .data_node_id import DataNodeId, Edit


class _AbstractSQLDataNode(DataNode, _TabularDataNodeMixin):
    """Abstract base class for data node implementations (SQLDataNode and SQLTableDataNode) that use SQL."""

    __STORAGE_TYPE = "NOT_IMPLEMENTED"
    __DB_NAME_KEY = "db_name"
    __DB_USERNAME_KEY = "db_username"
    __DB_PASSWORD_KEY = "db_password"
    __DB_HOST_KEY = "db_host"
    __DB_PORT_KEY = "db_port"
    __DB_ENGINE_KEY = "db_engine"
    __DB_DRIVER_KEY = "db_driver"
    __DB_EXTRA_ARGS_KEY = "db_extra_args"
    __SQLITE_FOLDER_PATH = "sqlite_folder_path"
    __SQLITE_FILE_EXTENSION = "sqlite_file_extension"

    __ENGINE_PROPERTIES: List[str] = [
        __DB_NAME_KEY,
        __DB_USERNAME_KEY,
        __DB_PASSWORD_KEY,
        __DB_HOST_KEY,
        __DB_PORT_KEY,
        __DB_DRIVER_KEY,
        __DB_EXTRA_ARGS_KEY,
        __SQLITE_FOLDER_PATH,
        __SQLITE_FILE_EXTENSION,
    ]

    __DB_HOST_DEFAULT = "localhost"
    __DB_PORT_DEFAULT = 1433
    __DB_DRIVER_DEFAULT = ""
    __SQLITE_FOLDER_PATH_DEFAULT = ""
    __SQLITE_FILE_EXTENSION_DEFAULT = ".db"

    __ENGINE_MSSQL = "mssql"
    __ENGINE_SQLITE = "sqlite"
    __ENGINE_MYSQL = "mysql"
    __ENGINE_POSTGRESQL = "postgresql"

    _ENGINE_REQUIRED_PROPERTIES: Dict[str, List[str]] = {
        __ENGINE_MSSQL: [__DB_USERNAME_KEY, __DB_PASSWORD_KEY, __DB_NAME_KEY],
        __ENGINE_MYSQL: [__DB_USERNAME_KEY, __DB_PASSWORD_KEY, __DB_NAME_KEY],
        __ENGINE_POSTGRESQL: [__DB_USERNAME_KEY, __DB_PASSWORD_KEY, __DB_NAME_KEY],
        __ENGINE_SQLITE: [__DB_NAME_KEY],
    }

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
        self._check_required_properties(properties)

        properties[self._EXPOSED_TYPE_PROPERTY] = _TabularDataNodeMixin._get_valid_exposed_type(properties)
        self._check_exposed_type(properties[self._EXPOSED_TYPE_PROPERTY])

        DataNode.__init__(
            self,
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
            **properties,
        )
        _TabularDataNodeMixin.__init__(self, **properties)
        self._engine = None
        if not self._last_edit_date:  # type: ignore
            self._last_edit_date = datetime.now()

        self._TAIPY_PROPERTIES.update(
            {
                self.__DB_NAME_KEY,
                self.__DB_USERNAME_KEY,
                self.__DB_PASSWORD_KEY,
                self.__DB_HOST_KEY,
                self.__DB_PORT_KEY,
                self.__DB_ENGINE_KEY,
                self.__DB_DRIVER_KEY,
                self.__DB_EXTRA_ARGS_KEY,
                self.__SQLITE_FOLDER_PATH,
                self.__SQLITE_FILE_EXTENSION,
                self._EXPOSED_TYPE_PROPERTY,
            }
        )

    def __setattr__(self, key: str, value) -> None:
        if key in self.__ENGINE_PROPERTIES:
            self._engine = None
        return super().__setattr__(key, value)

    def filter(self, operators: Optional[Union[List, Tuple]] = None, join_operator=JoinOperator.AND):
        properties = self.properties
        if properties[self._EXPOSED_TYPE_PROPERTY] == self._EXPOSED_TYPE_PANDAS:
            return self._read_as_pandas_dataframe(operators=operators, join_operator=join_operator)
        if properties[self._EXPOSED_TYPE_PROPERTY] == self._EXPOSED_TYPE_NUMPY:
            return self._read_as_numpy(operators=operators, join_operator=join_operator)
        return self._read_as(operators=operators, join_operator=join_operator)

    def _check_required_properties(self, properties: Dict):
        db_engine = properties.get(self.__DB_ENGINE_KEY)
        if not db_engine:
            raise MissingRequiredProperty(f"{self.__DB_ENGINE_KEY} is required.")
        if db_engine not in self._ENGINE_REQUIRED_PROPERTIES.keys():
            raise UnknownDatabaseEngine(f"Unknown engine: {db_engine}")
        required = self._ENGINE_REQUIRED_PROPERTIES[db_engine]

        if missing := set(required) - set(properties.keys()):
            raise MissingRequiredProperty(
                f"The following properties {', '.join(missing)} were not informed and are required."
            )

    def _get_engine(self):
        if self._engine is None:
            self._engine = create_engine(self._conn_string())
        return self._engine

    def _conn_string(self) -> str:
        properties = self.properties
        engine = properties.get(self.__DB_ENGINE_KEY)

        if self.__DB_USERNAME_KEY in self._ENGINE_REQUIRED_PROPERTIES[engine]:
            username = properties.get(self.__DB_USERNAME_KEY)
            username = urllib.parse.quote_plus(username)

        if self.__DB_PASSWORD_KEY in self._ENGINE_REQUIRED_PROPERTIES[engine]:
            password = properties.get(self.__DB_PASSWORD_KEY)
            password = urllib.parse.quote_plus(password)

        if self.__DB_NAME_KEY in self._ENGINE_REQUIRED_PROPERTIES[engine]:
            db_name = properties.get(self.__DB_NAME_KEY)
            db_name = urllib.parse.quote_plus(db_name)

        host = properties.get(self.__DB_HOST_KEY, self.__DB_HOST_DEFAULT)
        port = properties.get(self.__DB_PORT_KEY, self.__DB_PORT_DEFAULT)
        driver = properties.get(self.__DB_DRIVER_KEY, self.__DB_DRIVER_DEFAULT)
        extra_args = properties.get(self.__DB_EXTRA_ARGS_KEY, {})

        if driver:
            extra_args = {**extra_args, "driver": driver}
        for k, v in extra_args.items():
            extra_args[k] = re.sub(r"\s+", "+", v)
        extra_args_str = "&".join(f"{k}={str(v)}" for k, v in extra_args.items())

        if engine == self.__ENGINE_MSSQL:
            return f"mssql+pyodbc://{username}:{password}@{host}:{port}/{db_name}?{extra_args_str}"
        elif engine == self.__ENGINE_MYSQL:
            return f"mysql+pymysql://{username}:{password}@{host}:{port}/{db_name}?{extra_args_str}"
        elif engine == self.__ENGINE_POSTGRESQL:
            return f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{db_name}?{extra_args_str}"
        elif engine == self.__ENGINE_SQLITE:
            folder_path = properties.get(self.__SQLITE_FOLDER_PATH, self.__SQLITE_FOLDER_PATH_DEFAULT)
            file_extension = properties.get(self.__SQLITE_FILE_EXTENSION, self.__SQLITE_FILE_EXTENSION_DEFAULT)
            return "sqlite:///" + os.path.join(folder_path, f"{db_name}{file_extension}")
        raise UnknownDatabaseEngine(f"Unknown engine: {engine}")

    def _read(self):
        properties = self.properties
        if properties[self._EXPOSED_TYPE_PROPERTY] == self._EXPOSED_TYPE_PANDAS:
            return self._read_as_pandas_dataframe()
        if properties[self._EXPOSED_TYPE_PROPERTY] == self._EXPOSED_TYPE_NUMPY:
            return self._read_as_numpy()
        return self._read_as()

    def _read_as(self, operators: Optional[Union[List, Tuple]] = None, join_operator=JoinOperator.AND):
        custom_class = self.properties[self._EXPOSED_TYPE_PROPERTY]
        with self._get_engine().connect() as connection:
            query_result = connection.execute(text(self._get_read_query(operators, join_operator)))
        return [custom_class(**row) for row in query_result]

    def _read_as_numpy(
        self, operators: Optional[Union[List, Tuple]] = None, join_operator=JoinOperator.AND
    ) -> np.ndarray:
        return self._read_as_pandas_dataframe(operators=operators, join_operator=join_operator).to_numpy()

    def _read_as_pandas_dataframe(
        self,
        columns: Optional[List[str]] = None,
        operators: Optional[Union[List, Tuple]] = None,
        join_operator=JoinOperator.AND,
    ):
        with self._get_engine().connect() as conn:
            result = conn.execute(text(self._get_read_query(operators, join_operator)))

            # On pandas 1.3.5 there's a bug that makes that the dataframe from sqlalchemy query is
            # created without headers
            keys = list(result.keys())
            if columns:
                return pd.DataFrame(result, columns=keys)[columns]
            return pd.DataFrame(result, columns=keys)

    @abstractmethod
    def _get_read_query(self, operators: Optional[Union[List, Tuple]] = None, join_operator=JoinOperator.AND):
        query = self._get_base_read_query()

        if not operators:
            return query

        if not isinstance(operators, List):
            operators = [operators]

        conditions = []
        for key, value, operator in operators:
            if operator == Operator.EQUAL:
                conditions.append(f"{key} = '{value}'")
            elif operator == Operator.NOT_EQUAL:
                conditions.append(f"{key} <> '{value}'")
            elif operator == Operator.GREATER_THAN:
                conditions.append(f"{key} > '{value}'")
            elif operator == Operator.GREATER_OR_EQUAL:
                conditions.append(f"{key} >= '{value}'")
            elif operator == Operator.LESS_THAN:
                conditions.append(f"{key} < '{value}'")
            elif operator == Operator.LESS_OR_EQUAL:
                conditions.append(f"{key} <= '{value}'")

        if join_operator == JoinOperator.AND:
            query += f" WHERE {' AND '.join(conditions)}"
        elif join_operator == JoinOperator.OR:
            query += f" WHERE {' OR '.join(conditions)}"
        else:
            raise NotImplementedError(f"Join operator {join_operator} not implemented.")

        return query

    @abstractmethod
    def _get_base_read_query(self) -> str:
        raise NotImplementedError

    def _append(self, data) -> None:
        engine = self._get_engine()
        with engine.connect() as connection:
            with connection.begin() as transaction:
                try:
                    self._do_append(data, engine, connection)
                except Exception as e:
                    transaction.rollback()
                    raise e
                else:
                    transaction.commit()

    @abstractmethod
    def _do_append(self, data, engine, connection) -> None:
        raise NotImplementedError

    def _write(self, data) -> None:
        """Check data against a collection of types to handle insertion on the database."""
        engine = self._get_engine()
        with engine.connect() as connection:
            with connection.begin() as transaction:
                try:
                    self._do_write(data, engine, connection)
                except Exception as e:
                    transaction.rollback()
                    raise e
                else:
                    transaction.commit()

    @abstractmethod
    def _do_write(self, data, engine, connection) -> None:
        raise NotImplementedError

