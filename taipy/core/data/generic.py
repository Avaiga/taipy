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

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set

from taipy.common.config.common.scope import Scope

from .._version._version_manager_factory import _VersionManagerFactory
from ..exceptions.exceptions import MissingReadFunction, MissingRequiredProperty, MissingWriteFunction
from .data_node import DataNode
from .data_node_id import DataNodeId, Edit


class GenericDataNode(DataNode):
    """Generic Data Node that uses custom read and write functions.

    The read and write functions for this data node type are Python functions.

    The *properties* attribute must contain at least one of the two following entries:

    - *read_fct* (`Callable`): The read function for the data node.
    - *write_fct* (`Callable`): The write function for the data node.

    The *properties* attribute can also contain the following optional entries:

    - *read_fct_args* (`List[Any]`): The arguments to be passed to the read function.
    - *write_fct_args* (`List[Any]`): The arguments to be passed to the write function.
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
    ) -> None:
        if properties is None:
            properties = {}
        if missing := set(self._REQUIRED_PROPERTIES) - set(properties.keys()):
            raise MissingRequiredProperty(
                f"The following properties {', '.join(missing)} were not informed and are required."
            )

        missing_optional_fcts = set(self._REQUIRED_AT_LEAST_ONE_PROPERTY) - set(properties.keys())
        if len(missing_optional_fcts) == len(self._REQUIRED_AT_LEAST_ONE_PROPERTY):
            raise MissingRequiredProperty(
                f"None of the following properties {', '.join(missing)} were informed"
                "and at least one must be populated."
            )
        for missing_optional_fct in missing_optional_fcts:
            properties[missing_optional_fct] = None

        super().__init__(
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
        if not self._last_edit_date:  # type: ignore
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
        """Returns the storage type of the data node: "generic"."""
        return cls.__STORAGE_TYPE

    def _read(self):
        properties = self.properties
        if read_fct := properties[self._OPTIONAL_READ_FUNCTION_PROPERTY]:
            if read_fct_args := properties.get(self.__READ_FUNCTION_ARGS_PROPERTY, None):
                if not isinstance(read_fct_args, list):
                    return read_fct(*[read_fct_args])
                return read_fct(*read_fct_args)
            return read_fct()
        raise MissingReadFunction(f"The read function is not defined in data node config {self.config_id}.")

    def _write(self, data: Any):
        properties = self.properties
        if write_fct := properties[self._OPTIONAL_WRITE_FUNCTION_PROPERTY]:
            if write_fct_args := properties.get(self.__WRITE_FUNCTION_ARGS_PROPERTY, None):
                if not isinstance(write_fct_args, list):
                    return write_fct(data, *[write_fct_args])
                return write_fct(data, *write_fct_args)
            return write_fct(data)
        raise MissingWriteFunction(f"The write function is not defined in data node config {self.config_id}.")
