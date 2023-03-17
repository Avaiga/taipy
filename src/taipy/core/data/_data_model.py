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
from dataclasses import dataclass
from datetime import datetime, timedelta
from pydoc import locate
from typing import Any, Dict, List, Optional, cast

from taipy.config.common.scope import Scope

from .._version._utils import _version_migration
from ..common._utils import _load_fct
from ..common._warnings import _warn_deprecated
from ..common.alias import Edit
from ..data import DataNode, GenericDataNode, JSONDataNode, SQLDataNode


def _to_edits_migration(job_ids: Optional[List[str]]) -> List[Edit]:
    "Migrate a list of job IDs to a list of Edits. Used to migrate data model from <=2.0 to >=2.1 version." ""
    _warn_deprecated("job_ids", suggest="edits")
    if not job_ids:
        return []
    # We can't guess what is the timestamp corresponding to a modification from its job_id...
    # So let's use the current time...
    timestamp = datetime.now()
    return [cast(Edit, dict(timestamp=timestamp, job_id=job_id)) for job_id in job_ids]


@dataclass
class _DataNodeModel:
    id: str
    config_id: str
    scope: Scope
    storage_type: str
    name: str
    owner_id: Optional[str]
    parent_ids: List[str]
    last_edit_date: Optional[str]
    edits: List[Edit]
    version: str
    validity_days: Optional[float]
    validity_seconds: Optional[float]
    edit_in_progress: bool
    data_node_properties: Dict[str, Any]

    _READ_FCT_NAME_KEY = "read_fct_name"
    _READ_FCT_MODULE_KEY = "read_fct_module"
    _WRITE_FCT_NAME_KEY = "write_fct_name"
    _WRITE_FCT_MODULE_KEY = "write_fct_module"
    _JSON_ENCODER_NAME_KEY = "encoder_name"
    _JSON_ENCODER_MODULE_KEY = "encoder_module"
    _JSON_DECODER_NAME_KEY = "decoder_name"
    _JSON_DECODER_MODULE_KEY = "decoder_module"
    _EXPOSED_TYPE_KEY = "exposed_type"
    _CUSTOM_DOCUMENT_KEY = "custom_document"
    _WRITE_QUERY_BUILDER_NAME_KEY = "write_query_builder_name"
    _WRITE_QUERY_BUILDER_MODULE_KEY = "write_query_builder_module"
    _VALID_STRING_EXPOSED_TYPES = ["numpy", "pandas", "modin"]

    def to_dict(self) -> Dict[str, Any]:
        return {**dataclasses.asdict(self), "scope": repr(self.scope)}

    @staticmethod
    def from_dict(data: Dict[str, Any]):
        dn_properties = data["data_node_properties"]
        # Used for compatibility between <=2.0 to >=2.1 versions.
        if data.get("cacheable"):
            dn_properties["cacheable"] = True
        return _DataNodeModel(
            id=data["id"],
            config_id=data["config_id"],
            scope=Scope._from_repr(data["scope"]),
            storage_type=data["storage_type"],
            name=data["name"],
            owner_id=data.get("owner_id", data.get("parent_id")),
            parent_ids=data.get("parent_ids", []),
            last_edit_date=data.get("last_edit_date", data.get("last_edition_date")),
            edits=data.get("edits", _to_edits_migration(data.get("job_ids"))),
            version=data["version"] if "version" in data.keys() else _version_migration(),
            validity_days=data["validity_days"],
            validity_seconds=data["validity_seconds"],
            edit_in_progress=bool(data.get("edit_in_progress", data.get("edition_in_progress", False))),
            data_node_properties=dn_properties,
        )

    @classmethod
    def _from_entity(cls, data_node: DataNode) -> "_DataNodeModel":
        properties = data_node._properties.data.copy()
        if data_node.storage_type() == GenericDataNode.storage_type():
            read_fct = data_node._properties.get(GenericDataNode._OPTIONAL_READ_FUNCTION_PROPERTY, None)
            properties[cls._READ_FCT_NAME_KEY] = read_fct.__name__ if read_fct else None
            properties[cls._READ_FCT_MODULE_KEY] = read_fct.__module__ if read_fct else None

            write_fct = data_node._properties.get(GenericDataNode._OPTIONAL_WRITE_FUNCTION_PROPERTY, None)
            properties[cls._WRITE_FCT_NAME_KEY] = write_fct.__name__ if write_fct else None
            properties[cls._WRITE_FCT_MODULE_KEY] = write_fct.__module__ if write_fct else None

            del (
                properties[GenericDataNode._OPTIONAL_READ_FUNCTION_PROPERTY],
                properties[GenericDataNode._OPTIONAL_WRITE_FUNCTION_PROPERTY],
            )

        if data_node.storage_type() == JSONDataNode.storage_type():
            encoder = data_node._properties.get(JSONDataNode._ENCODER_KEY)
            properties[cls._JSON_ENCODER_NAME_KEY] = encoder.__name__ if encoder else None
            properties[cls._JSON_ENCODER_MODULE_KEY] = encoder.__module__ if encoder else None
            properties.pop(JSONDataNode._ENCODER_KEY, None)

            decoder = data_node._properties.get(JSONDataNode._DECODER_KEY)
            properties[cls._JSON_DECODER_NAME_KEY] = decoder.__name__ if decoder else None
            properties[cls._JSON_DECODER_MODULE_KEY] = decoder.__module__ if decoder else None
            properties.pop(JSONDataNode._DECODER_KEY, None)

        if data_node.storage_type() == SQLDataNode.storage_type():
            query_builder = data_node._properties.get(SQLDataNode._WRITE_QUERY_BUILDER_KEY)
            properties[cls._WRITE_QUERY_BUILDER_NAME_KEY] = query_builder.__name__ if query_builder else None
            properties[cls._WRITE_QUERY_BUILDER_MODULE_KEY] = query_builder.__module__ if query_builder else None
            properties.pop(SQLDataNode._WRITE_QUERY_BUILDER_KEY, None)

        if cls._EXPOSED_TYPE_KEY in properties.keys():
            if not isinstance(properties[cls._EXPOSED_TYPE_KEY], str):
                if isinstance(properties[cls._EXPOSED_TYPE_KEY], Dict):
                    properties[cls._EXPOSED_TYPE_KEY] = {
                        k: v if v in cls._VALID_STRING_EXPOSED_TYPES else f"{v.__module__}.{v.__qualname__}"
                        for k, v in properties[cls._EXPOSED_TYPE_KEY].items()
                    }
                elif isinstance(properties[cls._EXPOSED_TYPE_KEY], List):
                    properties[cls._EXPOSED_TYPE_KEY] = [
                        v if v in cls._VALID_STRING_EXPOSED_TYPES else f"{v.__module__}.{v.__qualname__}"
                        for v in properties[cls._EXPOSED_TYPE_KEY]
                    ]
                else:
                    properties[cls._EXPOSED_TYPE_KEY] = (
                        f"{properties[cls._EXPOSED_TYPE_KEY].__module__}."
                        f"{properties[cls._EXPOSED_TYPE_KEY].__qualname__}"
                    )

        if cls._CUSTOM_DOCUMENT_KEY in properties.keys():
            properties[cls._CUSTOM_DOCUMENT_KEY] = (
                f"{properties[cls._CUSTOM_DOCUMENT_KEY].__module__}."
                f"{properties[cls._CUSTOM_DOCUMENT_KEY].__qualname__}"
            )

        return _DataNodeModel(
            data_node.id,
            data_node.config_id,
            data_node._scope,
            data_node.storage_type(),
            data_node._name,
            data_node.owner_id,
            list(data_node._parent_ids),
            data_node._last_edit_date.isoformat() if data_node._last_edit_date else None,
            data_node._edits,
            data_node._version,
            data_node._validity_period.days if data_node._validity_period else None,
            data_node._validity_period.seconds if data_node._validity_period else None,
            data_node._edit_in_progress,
            properties,
        )

    def _to_entity(self):
        if self.storage_type == GenericDataNode.storage_type():
            if self.data_node_properties[self._READ_FCT_MODULE_KEY]:
                self.data_node_properties[GenericDataNode._OPTIONAL_READ_FUNCTION_PROPERTY] = _load_fct(
                    self.data_node_properties[self._READ_FCT_MODULE_KEY],
                    self.data_node_properties[self._READ_FCT_NAME_KEY],
                )
            else:
                self.data_node_properties[GenericDataNode._OPTIONAL_READ_FUNCTION_PROPERTY] = None

            if self.data_node_properties[self._WRITE_FCT_MODULE_KEY]:
                self.data_node_properties[GenericDataNode._OPTIONAL_WRITE_FUNCTION_PROPERTY] = _load_fct(
                    self.data_node_properties[self._WRITE_FCT_MODULE_KEY],
                    self.data_node_properties[self._WRITE_FCT_NAME_KEY],
                )
            else:
                self.data_node_properties[GenericDataNode._OPTIONAL_WRITE_FUNCTION_PROPERTY] = None

            del self.data_node_properties[self._READ_FCT_NAME_KEY]
            del self.data_node_properties[self._READ_FCT_MODULE_KEY]
            del self.data_node_properties[self._WRITE_FCT_NAME_KEY]
            del self.data_node_properties[self._WRITE_FCT_MODULE_KEY]

        if self.storage_type == JSONDataNode.storage_type():
            if self.data_node_properties[self._JSON_ENCODER_MODULE_KEY]:
                self.data_node_properties[JSONDataNode._ENCODER_KEY] = _load_fct(
                    self.data_node_properties[self._JSON_ENCODER_MODULE_KEY],
                    self.data_node_properties[self._JSON_ENCODER_NAME_KEY],
                )
            else:
                self.data_node_properties[JSONDataNode._ENCODER_KEY] = None

            if self.data_node_properties[self._JSON_DECODER_MODULE_KEY]:
                self.data_node_properties[JSONDataNode._DECODER_KEY] = _load_fct(
                    self.data_node_properties[self._JSON_DECODER_MODULE_KEY],
                    self.data_node_properties[self._JSON_DECODER_NAME_KEY],
                )
            else:
                self.data_node_properties[JSONDataNode._DECODER_KEY] = None

            del self.data_node_properties[self._JSON_ENCODER_NAME_KEY]
            del self.data_node_properties[self._JSON_ENCODER_MODULE_KEY]
            del self.data_node_properties[self._JSON_DECODER_NAME_KEY]
            del self.data_node_properties[self._JSON_DECODER_MODULE_KEY]

        if self.storage_type == SQLDataNode.storage_type():
            if self.data_node_properties[self._WRITE_QUERY_BUILDER_MODULE_KEY]:
                self.data_node_properties[SQLDataNode._WRITE_QUERY_BUILDER_KEY] = _load_fct(
                    self.data_node_properties[self._WRITE_QUERY_BUILDER_MODULE_KEY],
                    self.data_node_properties[self._WRITE_QUERY_BUILDER_NAME_KEY],
                )
            else:
                self.data_node_properties[SQLDataNode._WRITE_QUERY_BUILDER_KEY] = None

            del self.data_node_properties[self._WRITE_QUERY_BUILDER_NAME_KEY]
            del self.data_node_properties[self._WRITE_QUERY_BUILDER_MODULE_KEY]

        if self._EXPOSED_TYPE_KEY in self.data_node_properties.keys():
            if self.data_node_properties[self._EXPOSED_TYPE_KEY] not in self._VALID_STRING_EXPOSED_TYPES:
                if isinstance(self.data_node_properties[self._EXPOSED_TYPE_KEY], str):
                    self.data_node_properties[self._EXPOSED_TYPE_KEY] = locate(
                        self.data_node_properties[self._EXPOSED_TYPE_KEY]
                    )
                elif isinstance(self.data_node_properties[self._EXPOSED_TYPE_KEY], Dict):
                    self.data_node_properties[self._EXPOSED_TYPE_KEY] = {
                        k: v if v in self._VALID_STRING_EXPOSED_TYPES else locate(v)
                        for k, v in self.data_node_properties[self._EXPOSED_TYPE_KEY].items()
                    }
                elif isinstance(self.data_node_properties[self._EXPOSED_TYPE_KEY], List):
                    self.data_node_properties[self._EXPOSED_TYPE_KEY] = [
                        v if v in self._VALID_STRING_EXPOSED_TYPES else locate(v)
                        for v in self.data_node_properties[self._EXPOSED_TYPE_KEY]
                    ]

        if self._CUSTOM_DOCUMENT_KEY in self.data_node_properties.keys():
            if isinstance(self.data_node_properties[self._CUSTOM_DOCUMENT_KEY], str):
                self.data_node_properties[self._CUSTOM_DOCUMENT_KEY] = locate(
                    self.data_node_properties[self._CUSTOM_DOCUMENT_KEY]
                )

        validity_period = None
        if self.validity_seconds is not None and self.validity_days is not None:
            validity_period = timedelta(days=self.validity_days, seconds=self.validity_seconds)

        return DataNode._class_map()[self.storage_type](
            config_id=self.config_id,
            scope=self.scope,
            id=self.id,
            name=self.name,
            owner_id=self.owner_id,
            parent_ids=set(self.parent_ids),
            last_edit_date=datetime.fromisoformat(self.last_edit_date) if self.last_edit_date else None,
            edits=self.edits,
            version=self.version,
            validity_period=validity_period,
            edit_in_progress=self.edit_in_progress,
            properties=self.data_node_properties,
        )
