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

import os
import pathlib
import pickle
from datetime import datetime, timedelta
from typing import Any, List, Optional

from taipy.config.data_node.scope import Scope

from .data_node import DataNode
from ..common._reload import _self_reload
from ..common._warnings import _warn_deprecated
from ..common.alias import DataNodeId, JobId


class PickleDataNode(DataNode):
    """Data Node stored as a pickle file.

    Attributes:
        config_id (str): Identifier of the data node configuration. It must be a valid Python
            identifer.
        scope (Scope^): The scope of this data node.
        id (str): The unique identifier of this data node.
        name (str): A user-readable name of this data node.
        parent_id (str): The identifier of the parent (pipeline_id, scenario_id, cycle_id) or
            `None`.
        last_edit_date (datetime): The date and time of the last modification.
        job_ids (List[str]): The ordered list of jobs that have written this data node.
        validity_period (Optional[timedelta]): The validity period of a cacheable data node.
            Implemented as a timedelta. If _validity_period_ is set to None, the data_node is
            always up-to-date.
        edit_in_progress (bool): True if a task computing the data node has been submitted
            and not completed yet. False otherwise.
        properties (dict[str, Any]): A dictionary of additional properties.
            When creating a pickle data node, if the _properties_ dictionary contains a
            _"default_data"_ entry, the data node is automatically written with the corresponding
            _"default_data"_ value.
            If the _properties_ dictionary contains a _"path"_ entry, the data will be stored
            using the corresponding value as the name of the pickle file.
    """

    __STORAGE_TYPE = "pickle"
    __PICKLE_PATH_KEY = "path"
    __PICKLE_DEFAULT_PATH_KEY = "default_path"
    __DEFAULT_DATA_VALUE = "default_data"
    _REQUIRED_PROPERTIES: List[str] = []

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
        properties=None,
    ):
        if properties is None:
            properties = {}
        default_value = properties.pop(self.__DEFAULT_DATA_VALUE, None)
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
        self.__is_file_generated = False
        self._pickle_path = self.__build_path()
        if not self._last_edit_date and os.path.exists(self._pickle_path):
            self.unlock_edit()
        if default_value is not None and not os.path.exists(self._pickle_path):
            self.write(default_value)

    @classmethod
    def storage_type(cls) -> str:
        return cls.__STORAGE_TYPE

    @property  # type: ignore
    @_self_reload(DataNode._MANAGER_NAME)
    def path(self) -> Any:
        return self._pickle_path

    @path.setter  # type: ignore
    def path(self, value):
        self.properties[self.__PICKLE_DEFAULT_PATH_KEY] = value
        self.__is_file_generated = False

    @property
    def is_file_generated(self) -> bool:
        return self.__is_file_generated

    def _read(self):
        return pickle.load(open(self._pickle_path, "rb"))

    def _write(self, data):
        pickle.dump(data, open(self._pickle_path, "wb"))

    def __build_path(self):
        if file_name := self._properties.get(self.__PICKLE_DEFAULT_PATH_KEY):
            return file_name
        if file_name := self._properties.get(self.__PICKLE_PATH_KEY):
            _warn_deprecated("path", suggest="default_path")
            return file_name
        from taipy.config.config import Config

        dir_path = pathlib.Path(Config.global_config.storage_folder) / "pickles"
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
        self.__is_file_generated = True
        return dir_path / f"{self.id}.p"
