from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd
from sqlalchemy import create_engine

from taipy.common.alias import JobId
from taipy.data import DataSource, Scope
from taipy.exceptions import UnknownDatabaseEngine


class SQLDataSource(DataSource):
    """
    A class that represents a Data Source stored in a SQL database table.

    Attributes
    ----------
    config_name: str
        Name that identifies the data source. We strongly recommend to use lowercase alphanumeric characters,
        dash character '-', or underscore character '_'.
        Note that other characters are replaced according the following rules :
        - Space character ' ' is replaced by '_'
        - Unicode characters are replaced by a corresponding alphanumeric character using unicode library
        - Other characters are replaced by dash character '-'
    scope: Scope
        Scope Enum that refers to the scope of usage of the data source
    id: str
        Unique identifier of the data source
    parent_id: str
        Identifier of the parent (pipeline_id, scenario_id, bucket_id, None)
    last_edition_date: datetime
        Date and time of the last edition
    job_ids: List[str]
        Ordered list of jobs that have written the data source
    up_to_date: bool
        True if the data is considered as up to date. False otherwise.
    properties: dict
        list of additional arguments. Note that the properties parameter should at least contain values for "path" and
        "has_header" properties.
    """

    __TYPE = "sql"

    def __init__(
        self,
        config_name: str,
        scope: Scope,
        id: Optional[str] = None,
        parent_id: Optional[str] = None,
        last_edition_date: Optional[datetime] = None,
        job_ids: List[JobId] = None,
        up_to_date: bool = False,
        properties: Dict = None,
    ):
        if properties is None:
            properties = {}

        self.__engine = self.__create_engine(
            properties.get("db_username"),
            properties.get("db_password"),
            properties.get("db_name"),
            properties.get("db_engine"),
        )

        super().__init__(
            config_name,
            scope,
            id,
            parent_id,
            last_edition_date,
            job_ids or [],
            up_to_date,
            username=properties.get("db_username"),
            password=properties.get("db_password"),
            database=properties.get("db_name"),
            engine=properties.get("db_engine"),
            query=properties.get("query"),
        )

    @staticmethod
    def __build_conn_string(engine, username, password, database):
        # TODO: Add support to other SQL engines
        if engine == "mssql":
            return f"{engine}+pyodbc://{username}:{password}@{database}"
        raise UnknownDatabaseEngine(f"Unknown engine: {engine}")

    def __create_engine(self, engine, username, password, database):
        return create_engine(self.__build_conn_string(engine, username, password, database))

    @classmethod
    def type(cls) -> str:
        return cls.__TYPE

    def preview(self):
        pd.read_sql_query(self.query, con=self.__engine, chunksize=10)

    def _read(self, query=None):
        return pd.read_sql_query(self.query, con=self.__engine)

    def _write(self, data):
        pass
