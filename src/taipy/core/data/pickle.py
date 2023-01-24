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

import os
import pathlib
import pickle
from datetime import datetime, timedelta
from typing import Any, List, Optional, Set

import modin.pandas as pd

from taipy.config.common.scope import Scope

from .._version._version_manager_factory import _VersionManagerFactory
from ..common._reload import _self_reload
from ..common.alias import DataNodeId, Edit
from .data_node import DataNode


class PickleDataNode(DataNode):
    """Data Node stored as a pickle file.

    Attributes:
        config_id (str): Identifier of the data node configuration. It must be a valid Python
            identifer.
        scope (Scope^): The scope of this data node.
        id (str): The unique identifier of this data node.
        name (str): A user-readable name of this data node.
        owner_id (str): The identifier of the owner (pipeline_id, scenario_id, cycle_id) or
            `None`.
        parent_ids (Optional[Set[str]]): The identifiers of the parent tasks or `None`.
        last_edit_date (datetime): The date and time of the last modification.
        edits (List[Edit^]): The ordered list of edits for that job.
        version (str): The string indicates the application version of the data node to instantiate. If not provided,
            the current version is used.
        validity_period (Optional[timedelta]): The validity period of a data node.
            Implemented as a timedelta. If _validity_period_ is set to None, the data_node is
            always up-to-date.
        edit_in_progress (bool): True if a task computing the data node has been submitted
            and not completed yet. False otherwise.
        properties (dict[str, Any]): A dictionary of additional properties.
            When creating a pickle data node, if the _properties_ dictionary contains a
            _"default_data"_ entry, the data node is automatically written with the corresponding
            _"default_data"_ value.
            If the _properties_ dictionary contains a _"default_path"_ or _"path"_ entry, the data will be stored
            using the corresponding value as the name of the pickle file.
    """

    __STORAGE_TYPE = "pickle"
    __PATH_KEY = "path"
    __DEFAULT_PATH_KEY = "default_path"
    __DEFAULT_DATA_KEY = "default_data"
    __IS_GENERATED_KEY = "is_generated"
    _REQUIRED_PROPERTIES: List[str] = []

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
        properties=None,
    ):
        if properties is None:
            properties = {}
        default_value = properties.pop(self.__DEFAULT_DATA_KEY, None)
        self._path = properties.get(self.__PATH_KEY, properties.get(self.__DEFAULT_PATH_KEY))
        if self._path is not None:
            properties[self.__PATH_KEY] = self._path
        self._is_generated = properties.get(self.__IS_GENERATED_KEY, self._path is None)
        properties[self.__IS_GENERATED_KEY] = self._is_generated
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
            **properties,
        )
        if self._path is None:
            self._path = self.__build_path()
        if not self._last_edit_date and os.path.exists(self._path):
            self.last_edit_date = datetime.now()  # type: ignore
        if default_value is not None and not os.path.exists(self._path):
            self.write(default_value)

    @classmethod
    def storage_type(cls) -> str:
        return cls.__STORAGE_TYPE

    @property  # type: ignore
    @_self_reload(DataNode._MANAGER_NAME)
    def path(self) -> Any:
        return self._path

    @path.setter  # type: ignore
    def path(self, value):
        self._path = value
        self.properties[self.__PATH_KEY] = value
        self.properties[self.__IS_GENERATED_KEY] = False

    @property  # type: ignore
    @_self_reload(DataNode._MANAGER_NAME)
    def is_generated(self) -> bool:
        return self._is_generated

    def _read(self):
        os.environ["MODIN_PERSISTENT_PICKLE"] = "True"
        with open(self._path, "rb") as pf:
            return pickle.load(pf)

    def _write(self, data):
        if isinstance(data, (pd.DataFrame, pd.Series)):
            os.environ["MODIN_PERSISTENT_PICKLE"] = "True"
        with open(self._path, "wb") as pf:
            pickle.dump(data, pf)

    def __build_path(self):
        from taipy.config.config import Config

        dir_path = pathlib.Path(Config.global_config.storage_folder) / "pickles"
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
        return dir_path / f"{self.id}.p"
