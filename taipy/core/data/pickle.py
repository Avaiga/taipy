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

import pickle
from datetime import datetime, timedelta
from typing import Any, List, Optional, Set

from taipy.config.common.scope import Scope

from .._entity._reload import _Reloader
from .._version._version_manager_factory import _VersionManagerFactory
from ._file_datanode_mixin import _FileDataNodeMixin
from .data_node import DataNode
from .data_node_id import DataNodeId, Edit


class PickleDataNode(_FileDataNodeMixin, DataNode):
    """Data Node stored as a pickle file.

    Attributes:
        config_id (str): Identifier of the data node configuration. It must be a valid Python
            identifier.
        scope (Scope^): The scope of this data node.
        id (str): The unique identifier of this data node.
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
        properties (dict[str, Any]): A dictionary of additional properties.
            When creating a pickle data node, if the _properties_ dictionary contains a
            _"default_data"_ entry, the data node is automatically written with the corresponding
            _"default_data"_ value.
            If the _properties_ dictionary contains a _"default_path"_ or _"path"_ entry, the data will be stored
            using the corresponding value as the name of the pickle file.
    """

    __STORAGE_TYPE = "pickle"

    _REQUIRED_PROPERTIES: List[str] = []

    def __init__(
        self,
        config_id: str,
        scope: Scope,
        id: Optional[DataNodeId] = None,
        owner_id: Optional[str] = None,
        parent_ids: Optional[Set[str]] = None,
        last_edit_date: Optional[datetime] = None,
        edits: Optional[List[Edit]] = None,
        version: str = None,
        validity_period: Optional[timedelta] = None,
        edit_in_progress: bool = False,
        editor_id: Optional[str] = None,
        editor_expiration_date: Optional[datetime] = None,
        properties=None,
    ) -> None:
        self.id = id or self._new_id(config_id)

        if properties is None:
            properties = {}

        default_value = properties.pop(self._DEFAULT_DATA_KEY, None)
        _FileDataNodeMixin.__init__(self, properties)

        DataNode.__init__(
            self,
            config_id,
            scope,
            self.id,
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

        with _Reloader():
            self._write_default_data(default_value)

        self._TAIPY_PROPERTIES.update(
            {
                self._PATH_KEY,
                self._DEFAULT_PATH_KEY,
                self._DEFAULT_DATA_KEY,
                self._IS_GENERATED_KEY,
            }
        )

    @classmethod
    def storage_type(cls) -> str:
        return cls.__STORAGE_TYPE

    def _read(self):
        return self._read_from_path()

    def _read_from_path(self, path: Optional[str] = None, **read_kwargs) -> Any:
        if not path:
            path = self._path

        with open(path, "rb") as pf:
            return pickle.load(pf)

    def _write(self, data):
        with open(self._path, "wb") as pf:
            pickle.dump(data, pf)
