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

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
from sqlalchemy import MetaData, Table

from taipy.config.common.scope import Scope

from ..common.alias import DataNodeId, JobId
from ..exceptions.exceptions import MissingRequiredProperty
from .abstract_sql import AbstractSQLDataNode


class SQLTableDataNode(AbstractSQLDataNode):
    """Data Node stored in a SQL table.

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
            _"db_password"_, _"db_name"_, _"db_engine"_, _"table_name"_.
            For now, the accepted values for the _"db_engine"_ property are _"mssql"_ and
            _"sqlite"_.
    """

    __STORAGE_TYPE = "sql_table"
    __TABLE_KEY = "table_name"

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
        if properties.get(self.__TABLE_KEY) is None:
            raise MissingRequiredProperty(f"Property {self.__TABLE_KEY} is not informed and is required")
        super().__init__(
            config_id,
            scope,
            id=id,
            name=name,
            parent_id=parent_id,
            last_edit_date=last_edit_date,
            job_ids=job_ids,
            validity_period=validity_period,
            edit_in_progress=edit_in_progress,
            properties=properties,
        )

    @classmethod
    def storage_type(cls) -> str:
        return cls.__STORAGE_TYPE

    def _get_read_query(self):
        return f"SELECT * FROM {self.properties[self.__TABLE_KEY]}"

    def _do_write(self, data, engine, connection) -> None:
        table = self._create_table(engine)
        if isinstance(data, pd.DataFrame):
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
    def _insert_dataframe(df: pd.DataFrame, table: Any, connection: Any) -> None:
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
