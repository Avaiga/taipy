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
from typing import Dict, List, Optional

from taipy.config.common.scope import Scope

from ..common.alias import DataNodeId, JobId
from ..exceptions.exceptions import MissingRequiredProperty
from .abstract_sql import AbstractSQLDataNode


class SQLDataNode(AbstractSQLDataNode):
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
            _"db_password"_, _"db_name"_, _"db_engine"_, _"read_query"_, and _"write_query_builder"_.
            For now, the accepted values for the _"db_engine"_ property are _"mssql"_ and
            _"sqlite"_.
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
        parent_id: Optional[str] = None,
        last_edit_date: Optional[datetime] = None,
        job_ids: List[JobId] = None,
        validity_period: Optional[timedelta] = None,
        edit_in_progress: bool = False,
        properties: Dict = None,
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
            parent_id,
            last_edit_date,
            job_ids,
            validity_period,
            edit_in_progress,
            properties=properties,
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
