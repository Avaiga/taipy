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
from typing import Any, Dict, List, Optional, Set

from taipy.config.common.scope import Scope

from .._version._version_manager_factory import _VersionManagerFactory
from ..exceptions.exceptions import MissingReadFunction, MissingRequiredProperty, MissingWriteFunction
from .data_node import DataNode
from .data_node_id import DataNodeId, Edit


class GenericDataNode(DataNode):
    """Generic Data Node that uses custom read and write functions.

    The read and write function for this data node type can be implemented is Python.

    Attributes:
        config_id (str): Identifier of the data node configuration. It must be a valid Python
            identifier.
        scope (Scope^): The scope of this data node.
        id (str): The unique identifier of the data node.
        name (str): A user-readable name of the data node.
        owner_id (str): The identifier of the owner (sequence_id, scenario_id, cycle_id) or
            `None`.
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
            _properties_ parameter must at least contain an entry for either _"read_fct"_ or
            _"write_fct"_ representing the read and write functions.
            Entries for _"read_fct_args"_ and _"write_fct_args"_ respectively represent
            potential parameters for the _"read_fct"_ and _"write_fct"_ functions.
    """

    __STORAGE_TYPE = "generic"
    _OPTIONAL_READ_FUNCTION_PROPERTY = "read_fct"
    __READ_FUNCTION_ARGS_PROPERTY = "read_fct_args"
    _OPTIONAL_WRITE_FUNCTION_PROPERTY = "write_fct"
    __WRITE_FUNCTION_ARGS_PROPERTY = "write_fct_args"
    _REQUIRED_PROPERTIES: List[str] = []
    _REQUIRED_AT_LEAST_ONE_PROPERTY: List[str] = [_OPTIONAL_READ_FUNCTION_PROPERTY, _OPTIONAL_WRITE_FUNCTION_PROPERTY]

    def __init__(
        self,
        config_id: str,
        scope: Scope,
        id: Optional[DataNodeId] = None,
        name: Optional[str] = None,
        owner_id: Optional[str] = None,
        parent_ids: Optional[Set[str]] = None,
        last_edit_date: Optional[datetime] = None,
        edits: List[Edit] = None,
        version: str = None,
        validity_period: Optional[timedelta] = None,
        edit_in_progress: bool = False,
        editor_id: Optional[str] = None,
        editor_expiration_date: Optional[datetime] = None,
        properties: Dict = None,
    ):
        if properties is None:
            properties = {}
        if missing := set(self._REQUIRED_PROPERTIES) - set(properties.keys()):
            raise MissingRequiredProperty(
                f"The following properties " f"{', '.join(x for x in missing)} were not informed and are required."
            )

        missing_optional_fcts = set(self._REQUIRED_AT_LEAST_ONE_PROPERTY) - set(properties.keys())
        if len(missing_optional_fcts) == len(self._REQUIRED_AT_LEAST_ONE_PROPERTY):
            raise MissingRequiredProperty(
                f"None of the following properties "
                f"{', '.join(x for x in missing)} were informed and at least one must be populated."
            )
        for missing_optional_fct in missing_optional_fcts:
            properties[missing_optional_fct] = None

        super().__init__(
            config_id,
            scope,
            id,
            name,
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
        if not self._last_edit_date:
            self._last_edit_date = datetime.now()

        self._TAIPY_PROPERTIES.update(
            {
                self.__READ_FUNCTION_ARGS_PROPERTY,
                self.__WRITE_FUNCTION_ARGS_PROPERTY,
                self._OPTIONAL_READ_FUNCTION_PROPERTY,
                self._OPTIONAL_WRITE_FUNCTION_PROPERTY,
            }
        )

    @classmethod
    def storage_type(cls) -> str:
        return cls.__STORAGE_TYPE

    def _read(self):
        if read_fct := self.properties[self._OPTIONAL_READ_FUNCTION_PROPERTY]:
            if read_fct_args := self.properties.get(self.__READ_FUNCTION_ARGS_PROPERTY, None):
                if not isinstance(read_fct_args, list):
                    return read_fct(*[read_fct_args])
                return read_fct(*read_fct_args)
            return read_fct()
        raise MissingReadFunction(f"The read function is not defined in data node config {self.config_id}.")

    def _write(self, data: Any):
        if write_fct := self.properties[self._OPTIONAL_WRITE_FUNCTION_PROPERTY]:
            if write_fct_args := self.properties.get(self.__WRITE_FUNCTION_ARGS_PROPERTY, None):
                if not isinstance(write_fct_args, list):
                    return write_fct(data, *[write_fct_args])
                return write_fct(data, *write_fct_args)
            return write_fct(data)
        raise MissingWriteFunction(f"The write function is not defined in data node config {self.config_id}.")
