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
from .data_node import DataNode
from .data_node_id import DataNodeId, Edit

in_memory_storage: Dict[str, Any] = {}


class InMemoryDataNode(DataNode):
    """Data Node stored in memory.

    Warning:
        This Data Node implementation is not compatible with a parallel execution of taipy tasks,
        but only with a task executor in development mode. The purpose of `InMemoryDataNode` is
        mostly to be used for development, prototyping, or debugging.

    The *properties* attribute can also contain the following optional entries:

    - *default_data* (`Any`): The default data of the data node. It is used at the data node
        instantiation
    """

    __STORAGE_TYPE = "in_memory"
    __DEFAULT_DATA_VALUE = "default_data"
    _REQUIRED_PROPERTIES: List[str] = []

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
        properties=None,
    ) -> None:
        if properties is None:
            properties = {}
        default_value = properties.pop(self.__DEFAULT_DATA_VALUE, None)
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
        if default_value is not None and self.id not in in_memory_storage:
            self._write(default_value)
            self._last_edit_date = datetime.now()
            self._edits.append(
                Edit(
                    {
                        "timestamp": self._last_edit_date,
                        "editor": "TAIPY",
                        "comment": "Default data written.",
                    }
                )
            )

        self._TAIPY_PROPERTIES.update({self.__DEFAULT_DATA_VALUE})

    @classmethod
    def storage_type(cls) -> str:
        """Return the storage type of the data node: "in_memory"."""
        return cls.__STORAGE_TYPE

    def _read(self):
        return in_memory_storage.get(self.id)

    def _write(self, data):
        in_memory_storage[self.id] = data
