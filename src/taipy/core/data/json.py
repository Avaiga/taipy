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

import dataclasses
import json
import os
from datetime import date, datetime, timedelta
from enum import Enum
from os.path import isfile
from pydoc import locate
from typing import Any, Dict, List, Optional, Set

from taipy.config.common.scope import Scope

from .._backup._backup import replace_in_backup_file
from .._entity._reload import _self_reload
from .._version._version_manager_factory import _VersionManagerFactory
from .abstract_file import _AbstractFileDataNode
from .data_node import DataNode
from .data_node_id import DataNodeId, Edit


class JSONDataNode(DataNode, _AbstractFileDataNode):
    """Data Node stored as a JSON file.

    Attributes:
        config_id (str): Identifier of the data node configuration. This string must be a valid
            Python identifier.
        scope (Scope^): The scope of this data node.
        id (str): The unique identifier of this data node.
        name (str): A user-readable name of this data node.
        owner_id (str): The identifier of the owner (pipeline_id, scenario_id, cycle_id) or `None`.
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
        path (str): The path to the JSON file.
        encoder (json.JSONEncoder): The JSON encoder that is used to write into the JSON file.
        decoder (json.JSONDecoder): The JSON decoder that is used to read from the JSON file.
        properties (dict[str, Any]): A dictionary of additional properties. The _properties_
            must have a _"default_path"_ or _"path"_ entry with the path of the JSON file.
    """

    __STORAGE_TYPE = "json"
    __DEFAULT_DATA_KEY = "default_data"
    __DEFAULT_PATH_KEY = "default_path"
    __PATH_KEY = "path"
    _ENCODER_KEY = "encoder"
    _DECODER_KEY = "decoder"
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
        properties: Dict = None,
    ):
        if properties is None:
            properties = {}

        default_value = properties.pop(self.__DEFAULT_DATA_KEY, None)

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
        self._path = properties.get(self.__PATH_KEY, properties.get(self.__DEFAULT_PATH_KEY))
        if not self._path:
            self._path = self._build_path(self.storage_type())
        properties[self.__PATH_KEY] = self._path

        self._decoder = self._properties.get(self._DECODER_KEY, _DefaultJSONDecoder)
        self._encoder = self._properties.get(self._ENCODER_KEY, _DefaultJSONEncoder)

        if default_value is not None and not os.path.exists(self._path):
            self.write(default_value)

        if not self._last_edit_date and isfile(self._path):  # type: ignore
            self.last_edit_date = datetime.now()  # type: ignore

    @classmethod
    def storage_type(cls) -> str:
        return cls.__STORAGE_TYPE

    @property  # type: ignore
    @_self_reload(DataNode._MANAGER_NAME)
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        tmp_old_path = self._path
        self._path = value
        self.properties[self.__PATH_KEY] = value
        replace_in_backup_file(old_file_path=tmp_old_path, new_file_path=self._path)

    @property  # type: ignore
    @_self_reload(DataNode._MANAGER_NAME)
    def encoder(self):
        return self._encoder

    @encoder.setter
    def encoder(self, encoder: json.JSONEncoder):
        self.properties[self._ENCODER_KEY] = encoder

    @property  # type: ignore
    @_self_reload(DataNode._MANAGER_NAME)
    def decoder(self):
        return self._decoder

    @decoder.setter
    def decoder(self, decoder: json.JSONDecoder):
        self.properties[self._DECODER_KEY] = decoder

    def _read(self):
        with open(self._path, "r") as f:
            return json.load(f, cls=self._decoder)

    def _write(self, data: Any):
        with open(self._path, "w") as f:  # type: ignore
            json.dump(data, f, indent=4, cls=self._encoder)


class _DefaultJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Enum):
            return {
                "__type__": f"Enum-{o.__class__.__module__}-{o.__class__.__qualname__}-{o.name}",
                "__value__": o.value,
            }

        if isinstance(o, (datetime, date)):
            return {"__type__": "Datetime", "__value__": o.isoformat()}

        if dataclasses.is_dataclass(o):
            return {
                "__type__": f"dataclass-{o.__class__.__module__}-{o.__class__.__qualname__}",
                "__value__": dataclasses.asdict(o),
            }

        return super().default(o)


class _DefaultJSONDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, source):
        if _type := source.get("__type__"):
            if _type.startswith("Enum"):
                _, module, classname, name = _type.split("-")
                _enum_class = locate(f"{module}.{classname}")
                return _enum_class[name]

            if _type == "Datetime":
                return datetime.fromisoformat(source.get("__value__"))

            if _type.startswith("dataclass"):
                _, module, classname = _type.split("-")
                _data_class = locate(f"{module}.{classname}")
                return _data_class(**source.get("__value__"))

        return source
