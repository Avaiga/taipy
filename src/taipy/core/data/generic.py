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
from typing import Any, Dict, List, Optional

from taipy.config.data_node.scope import Scope

from .data_node import DataNode
from ..common.alias import DataNodeId, JobId
from ..exceptions.exceptions import MissingReadFunction, MissingRequiredProperty, MissingWriteFunction


class GenericDataNode(DataNode):
    """Generic Data Node that uses custom read and write functions.

    The read and write function for this data node type can be implemented is Python.

    Attributes:
        config_id (str): Identifier of the data node configuration. It must be a valid Python
            identifier.
        scope (Scope^): The scope of this data node.
        id (str): The unique identifier of the data node.
        name (str): A user-readable name of the data node.
        parent_id (str): The identifier of the parent (pipeline_id, scenario_id, cycle_id) or
            `None`.
        last_edit_date (datetime): The date and time of the last modification.
        job_ids (List[str]): The ordered list of jobs that have written this data node.
        validity_period (Optional[timedelta]): The validity period of a cacheable data node.
            Implemented as a timedelta. If _validity_period_ is set to None, the data node is
            always up-to-date.
        edit_in_progress (bool): True if a task computing the data node has been submitted
            and not completed yet. False otherwise.
        properties (dict[str, Any]): A dictionary of additional properties. Note that the
            _properties_ parameter must at least contain an entry for _"read_fct"_ or
            _"write_fct"_ representing the read and write functions.
            Entries for _"read_fct_params"_ and _"write_fct_params"_ respectively represent
            potential parameters for the _"read_fct"_ and _"write_fct"_ functions.
    """

    __STORAGE_TYPE = "generic"
    _REQUIRED_READ_FUNCTION_PROPERTY = "read_fct"
    _READ_FUNCTION_PARAMS_PROPERTY = "read_fct_params"
    _REQUIRED_WRITE_FUNCTION_PROPERTY = "write_fct"
    _WRITE_FUNCTION_PARAMS_PROPERTY = "write_fct_params"
    _REQUIRED_PROPERTIES: List[str] = [_REQUIRED_READ_FUNCTION_PROPERTY, _REQUIRED_WRITE_FUNCTION_PROPERTY]

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
        if missing := set(self._REQUIRED_PROPERTIES) - set(properties.keys()):
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

    @classmethod
    def storage_type(cls) -> str:
        return cls.__STORAGE_TYPE

    def _read(self):
        if read_fct := self.properties[self._REQUIRED_READ_FUNCTION_PROPERTY]:
            if self._READ_FUNCTION_PARAMS_PROPERTY in self.properties.keys():
                return read_fct(*self.properties[self._READ_FUNCTION_PARAMS_PROPERTY])
            return read_fct()
        raise MissingReadFunction

    def _write(self, data: Any):
        if write_fct := self.properties[self._REQUIRED_WRITE_FUNCTION_PROPERTY]:
            if self._WRITE_FUNCTION_PARAMS_PROPERTY in self.properties.keys():
                return write_fct(data, *self.properties[self._WRITE_FUNCTION_PARAMS_PROPERTY])
            return write_fct(data)
        raise MissingWriteFunction
