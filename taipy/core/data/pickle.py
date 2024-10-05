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

from taipy.common.config.common.scope import Scope

from .._entity._reload import _Reloader
from .._version._version_manager_factory import _VersionManagerFactory
from ._file_datanode_mixin import _FileDataNodeMixin
from .data_node import DataNode
from .data_node_id import DataNodeId, Edit


class PickleDataNode(DataNode, _FileDataNodeMixin):
    """Data Node stored as a pickle file.

    The *properties* attribute can contain the following optional entries:

    - *default_path* (`str`): The default path of the Pickle file used at the instantiation of the
        data node.
    - *default_data*: The default data of the data node. It is used at the data node instantiation
        to write the data to the Pickle file.
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
        """Return the storage type of the data node: "pickle"."""
        return cls.__STORAGE_TYPE

    def _read(self):
        return self._read_from_path()

    def _read_from_path(self, path: Optional[str] = None, **read_kwargs) -> Any:
        if path is None:
            path = self._path

        with open(path, "rb") as pf:
            return pickle.load(pf)

    def _write(self, data):
        with open(self._path, "wb") as pf:
            pickle.dump(data, pf)
