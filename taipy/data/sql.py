from datetime import datetime
from typing import Dict, List, Optional

import pandas as pd
from sqlalchemy import create_engine, text

from taipy.common.alias import DataSourceId, JobId
from taipy.data.data_source import DataSource
from taipy.data.scope import Scope
from taipy.exceptions import MissingRequiredProperty, UnknownDatabaseEngine


class SQLDataSource(DataSource):
    """
    A Data Source stored as a SQL database.

    Attributes:
        config_name (str):  Name that identifies the data source.
            We strongly recommend to use lowercase alphanumeric characters, dash character '-', or underscore character
            '_'. Note that other characters are replaced according the following rules :
            - Space characters are replaced by underscore characters ('_').
            - Unicode characters are replaced by a corresponding alphanumeric character using the Unicode library.
            - Other characters are replaced by dash characters ('-').
        scope (Scope):  The usage scope of this data source.
        id (str): Unique identifier of this data source.
        name (str): User-readable name of the data source.
        parent_id (str): Identifier of the parent (pipeline_id, scenario_id, cycle_id) or `None`.
        last_edition_date (datetime):  Date and time of the last edition.
        job_ids (List[str]): Ordered list of jobs that have written this data source.
        edition_in_progress (bool): True if a task computing the data source has been submitted and not completed yet.
            False otherwise.
        properties (list): List of additional arguments. Note that the properties parameter should at least contain
            values for "db_username", "db_password", "db_name", "db_engine" and "query" properties.
    """

    __STORAGE_TYPE = "sql"
    __EXPOSED_TYPE_PROPERTY = "exposed_type"
    __REQUIRED_PROPERTIES = ["db_username", "db_password", "db_name", "db_engine", "query"]

    def __init__(
        self,
        config_name: str,
        scope: Scope,
        id: Optional[DataSourceId] = None,
        name: Optional[str] = None,
        parent_id: Optional[str] = None,
        last_edition_date: Optional[datetime] = None,
        job_ids: List[JobId] = None,
        validity_days: Optional[int] = None,
        validity_hours: Optional[int] = None,
        validity_minutes: Optional[int] = None,
        edition_in_progress: bool = False,
        properties: Dict = None,
    ):
        if properties is None:
            properties = {}

        if missing := set(self.__REQUIRED_PROPERTIES) - set(properties.keys()):
            raise MissingRequiredProperty(
                f"The following properties " f"{', '.join(x for x in missing)} were not informed and are required"
            )

        self.__engine = self.__create_engine(
            properties.get("db_engine"),
            properties.get("db_username"),
            properties.get("db_password"),
            properties.get("db_name"),
        )

        super().__init__(
            config_name,
            scope,
            id,
            name,
            parent_id,
            last_edition_date,
            job_ids,
            validity_days,
            validity_hours,
            validity_minutes,
            edition_in_progress,
            **properties,
        )
        if not self.last_edition_date:
            self.unlock_edition()

    @staticmethod
    def __build_conn_string(engine, username, password, database):
        # TODO: Add support to other SQL engines
        if engine == "mssql":
            return f"{engine}+pyodbc://{username}:{password}@{database}"
        raise UnknownDatabaseEngine(f"Unknown engine: {engine}")

    def __create_engine(self, engine, username, password, database):
        return create_engine(self.__build_conn_string(engine, username, password, database))

    @classmethod
    def storage_type(cls) -> str:
        return cls.__STORAGE_TYPE

    def _read(self):
        if self.__EXPOSED_TYPE_PROPERTY in self.properties:
            return self._read_as(self.query, self.properties[self.__EXPOSED_TYPE_PROPERTY])
        return self._read_as_pandas_dataframe()

    def _read_as(self, query, custom_class):
        with self.__engine.connect() as connection:
            query_result = connection.execute(text(query))
        return list(map(lambda row: custom_class(**row), query_result))

    def _read_as_pandas_dataframe(self, columns: Optional[List[str]] = None):
        if columns:
            return pd.read_sql_query(self.query, con=self.__engine)[columns]
        return pd.read_sql_query(self.query, con=self.__engine)

    def _write(self, data):
        pass
