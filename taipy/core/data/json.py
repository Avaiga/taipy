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

import dataclasses
import json
from datetime import date, datetime, timedelta
from enum import Enum
from pydoc import locate
from typing import Any, Dict, List, Optional, Set

from taipy.common.config.common.scope import Scope

from .._entity._reload import _Reloader, _self_reload
from .._version._version_manager_factory import _VersionManagerFactory
from ._file_datanode_mixin import _FileDataNodeMixin
from .data_node import DataNode
from .data_node_id import DataNodeId, Edit


class JSONDataNode(DataNode, _FileDataNodeMixin):
    """Data Node stored as a JSON file.

    The *properties* attribute can contain the following optional entries:

    - *default_path* (`str`): The default path of the JSON file used at the instantiation of
        the data node.
    - *default_data* (`Any`): The default data of the data node. It is used at the data node
        instantiation to write the data to the JSON file.
    - *encoding* (`str`): The encoding of the JSON file. The default value is `utf-8`.\n
    """

    __STORAGE_TYPE = "json"
    __ENCODING_KEY = "encoding"
    _ENCODER_KEY = "encoder"
    _DECODER_KEY = "decoder"
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
        version: Optional[str] = None,
        validity_period: Optional[timedelta] = None,
        edit_in_progress: bool = False,
        editor_id: Optional[str] = None,
        editor_expiration_date: Optional[datetime] = None,
        properties: Optional[Dict] = None,
    ) -> None:
        self.id = id or self._new_id(config_id)

        if properties is None:
            properties = {}

        if self.__ENCODING_KEY not in properties.keys():
            properties[self.__ENCODING_KEY] = "utf-8"

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

        self._decoder = self._properties.get(self._DECODER_KEY, _DefaultJSONDecoder)
        self._encoder = self._properties.get(self._ENCODER_KEY, _DefaultJSONEncoder)

        with _Reloader():
            self._write_default_data(default_value)

        self._TAIPY_PROPERTIES.update(
            {
                self._PATH_KEY,
                self._DEFAULT_PATH_KEY,
                self._DEFAULT_DATA_KEY,
                self._IS_GENERATED_KEY,
                self.__ENCODING_KEY,
                self._ENCODER_KEY,
                self._DECODER_KEY,
            }
        )

    @classmethod
    def storage_type(cls) -> str:
        """Return the storage type of the data node: "json"."""
        return cls.__STORAGE_TYPE

    @property  # type: ignore
    @_self_reload(DataNode._MANAGER_NAME)
    def encoder(self) -> json.JSONEncoder:
        """The JSON encoder that is used to write into the JSON file."""
        return self._encoder

    @encoder.setter
    def encoder(self, encoder: json.JSONEncoder) -> None:
        self.properties[self._ENCODER_KEY] = encoder

    @property  # type: ignore
    @_self_reload(DataNode._MANAGER_NAME)
    def decoder(self) -> json.JSONDecoder:
        """The JSON decoder that is used to read from the JSON file."""
        return self._decoder

    @decoder.setter
    def decoder(self, decoder: json.JSONDecoder) -> None:
        self.properties[self._DECODER_KEY] = decoder

    def _read(self):
        return self._read_from_path()

    def _read_from_path(self, path: Optional[str] = None, **read_kwargs) -> Any:
        if path is None:
            path = self._path

        with open(path, "r", encoding=self.properties[self.__ENCODING_KEY]) as f:
            return json.load(f, cls=self._decoder)

    def _append(self, data: Any):
        with open(self._path, "r+", encoding=self.properties[self.__ENCODING_KEY]) as f:
            file_data = json.load(f, cls=self._decoder)
            if isinstance(file_data, List):
                if isinstance(data, List):
                    file_data.extend(data)
                else:
                    file_data.append(data)
            elif isinstance(data, Dict):
                file_data.update(data)

            f.seek(0)
            json.dump(file_data, f, indent=4, cls=self._encoder)

    def _write(self, data: Any):
        with open(self._path, "w", encoding=self.properties[self.__ENCODING_KEY]) as f:  # type: ignore
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
        json.JSONDecoder.__init__(self, *args, **kwargs, object_hook=self.object_hook)

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
