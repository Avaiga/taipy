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

import pathlib
from datetime import datetime, timedelta
from pydoc import locate
from typing import Any, Dict, Iterable, List, Optional, Union

from .._repository._repository import _AbstractRepository
from .._repository._repository_adapter import _RepositoryAdapter
from ..common._utils import _load_fct
from ._data_model import _DataNodeModel
from .data_node import DataNode
from .generic import GenericDataNode
from .json import JSONDataNode
from .sql import SQLDataNode


class _DataRepository(_AbstractRepository[_DataNodeModel, DataNode]):  # type: ignore
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

    def __init__(self, **kwargs):
        kwargs.update({"to_model_fct": self._to_model, "from_model_fct": self._from_model})
        self.repo = _RepositoryAdapter.select_base_repository()(**kwargs)
        self.class_map = DataNode._class_map()

    @property
    def repository(self):
        return self.repo

    def _to_model(self, data_node: DataNode):
        properties = data_node._properties.data.copy()
        if data_node.storage_type() == GenericDataNode.storage_type():
            read_fct = data_node._properties[GenericDataNode._REQUIRED_READ_FUNCTION_PROPERTY]
            properties[self._READ_FCT_NAME_KEY] = read_fct.__name__ if read_fct else None
            properties[self._READ_FCT_MODULE_KEY] = read_fct.__module__ if read_fct else None

            write_fct = data_node._properties[GenericDataNode._REQUIRED_WRITE_FUNCTION_PROPERTY]
            properties[self._WRITE_FCT_NAME_KEY] = write_fct.__name__ if write_fct else None
            properties[self._WRITE_FCT_MODULE_KEY] = write_fct.__module__ if write_fct else None

            del (
                properties[GenericDataNode._REQUIRED_READ_FUNCTION_PROPERTY],
                properties[GenericDataNode._REQUIRED_WRITE_FUNCTION_PROPERTY],
            )

        if data_node.storage_type() == JSONDataNode.storage_type():
            encoder = data_node._properties.get(JSONDataNode._ENCODER_KEY)
            properties[self._JSON_ENCODER_NAME_KEY] = encoder.__name__ if encoder else None
            properties[self._JSON_ENCODER_MODULE_KEY] = encoder.__module__ if encoder else None
            properties.pop(JSONDataNode._ENCODER_KEY, None)

            decoder = data_node._properties.get(JSONDataNode._DECODER_KEY)
            properties[self._JSON_DECODER_NAME_KEY] = decoder.__name__ if decoder else None
            properties[self._JSON_DECODER_MODULE_KEY] = decoder.__module__ if decoder else None
            properties.pop(JSONDataNode._DECODER_KEY, None)

        if data_node.storage_type() == SQLDataNode.storage_type():
            query_builder = data_node._properties.get(SQLDataNode._WRITE_QUERY_BUILDER_KEY)
            properties[self._WRITE_QUERY_BUILDER_NAME_KEY] = query_builder.__name__ if query_builder else None
            properties[self._WRITE_QUERY_BUILDER_MODULE_KEY] = query_builder.__module__ if query_builder else None
            properties.pop(SQLDataNode._WRITE_QUERY_BUILDER_KEY, None)

        if self._EXPOSED_TYPE_KEY in properties.keys():
            if not isinstance(properties[self._EXPOSED_TYPE_KEY], str):
                if isinstance(properties[self._EXPOSED_TYPE_KEY], Dict):
                    properties[self._EXPOSED_TYPE_KEY] = {
                        k: v if v in self._VALID_STRING_EXPOSED_TYPES else f"{v.__module__}.{v.__qualname__}"
                        for k, v in properties[self._EXPOSED_TYPE_KEY].items()
                    }
                elif isinstance(properties[self._EXPOSED_TYPE_KEY], List):
                    properties[self._EXPOSED_TYPE_KEY] = [
                        v if v in self._VALID_STRING_EXPOSED_TYPES else f"{v.__module__}.{v.__qualname__}"
                        for v in properties[self._EXPOSED_TYPE_KEY]
                    ]
                else:
                    properties[self._EXPOSED_TYPE_KEY] = (
                        f"{properties[self._EXPOSED_TYPE_KEY].__module__}."
                        f"{properties[self._EXPOSED_TYPE_KEY].__qualname__}"
                    )

        if self._CUSTOM_DOCUMENT_KEY in properties.keys():
            properties[self._CUSTOM_DOCUMENT_KEY] = (
                f"{properties[self._CUSTOM_DOCUMENT_KEY].__module__}."
                f"{properties[self._CUSTOM_DOCUMENT_KEY].__qualname__}"
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

    def _from_model(self, model: _DataNodeModel):
        if model.storage_type == GenericDataNode.storage_type():
            if model.data_node_properties[self._READ_FCT_MODULE_KEY]:
                model.data_node_properties[GenericDataNode._REQUIRED_READ_FUNCTION_PROPERTY] = _load_fct(
                    model.data_node_properties[self._READ_FCT_MODULE_KEY],
                    model.data_node_properties[self._READ_FCT_NAME_KEY],
                )
            else:
                model.data_node_properties[GenericDataNode._REQUIRED_READ_FUNCTION_PROPERTY] = None

            if model.data_node_properties[self._WRITE_FCT_MODULE_KEY]:
                model.data_node_properties[GenericDataNode._REQUIRED_WRITE_FUNCTION_PROPERTY] = _load_fct(
                    model.data_node_properties[self._WRITE_FCT_MODULE_KEY],
                    model.data_node_properties[self._WRITE_FCT_NAME_KEY],
                )
            else:
                model.data_node_properties[GenericDataNode._REQUIRED_WRITE_FUNCTION_PROPERTY] = None

            del model.data_node_properties[self._READ_FCT_NAME_KEY]
            del model.data_node_properties[self._READ_FCT_MODULE_KEY]
            del model.data_node_properties[self._WRITE_FCT_NAME_KEY]
            del model.data_node_properties[self._WRITE_FCT_MODULE_KEY]

        if model.storage_type == JSONDataNode.storage_type():
            if model.data_node_properties[self._JSON_ENCODER_MODULE_KEY]:
                model.data_node_properties[JSONDataNode._ENCODER_KEY] = _load_fct(
                    model.data_node_properties[self._JSON_ENCODER_MODULE_KEY],
                    model.data_node_properties[self._JSON_ENCODER_NAME_KEY],
                )
            else:
                model.data_node_properties[JSONDataNode._ENCODER_KEY] = None

            if model.data_node_properties[self._JSON_DECODER_MODULE_KEY]:
                model.data_node_properties[JSONDataNode._DECODER_KEY] = _load_fct(
                    model.data_node_properties[self._JSON_DECODER_MODULE_KEY],
                    model.data_node_properties[self._JSON_DECODER_NAME_KEY],
                )
            else:
                model.data_node_properties[JSONDataNode._DECODER_KEY] = None

            del model.data_node_properties[self._JSON_ENCODER_NAME_KEY]
            del model.data_node_properties[self._JSON_ENCODER_MODULE_KEY]
            del model.data_node_properties[self._JSON_DECODER_NAME_KEY]
            del model.data_node_properties[self._JSON_DECODER_MODULE_KEY]

        if model.storage_type == SQLDataNode.storage_type():
            if model.data_node_properties[self._WRITE_QUERY_BUILDER_MODULE_KEY]:
                model.data_node_properties[SQLDataNode._WRITE_QUERY_BUILDER_KEY] = _load_fct(
                    model.data_node_properties[self._WRITE_QUERY_BUILDER_MODULE_KEY],
                    model.data_node_properties[self._WRITE_QUERY_BUILDER_NAME_KEY],
                )
            else:
                model.data_node_properties[SQLDataNode._WRITE_QUERY_BUILDER_KEY] = None

            del model.data_node_properties[self._WRITE_QUERY_BUILDER_NAME_KEY]
            del model.data_node_properties[self._WRITE_QUERY_BUILDER_MODULE_KEY]

        if self._EXPOSED_TYPE_KEY in model.data_node_properties.keys():
            if model.data_node_properties[self._EXPOSED_TYPE_KEY] not in self._VALID_STRING_EXPOSED_TYPES:
                if isinstance(model.data_node_properties[self._EXPOSED_TYPE_KEY], str):
                    model.data_node_properties[self._EXPOSED_TYPE_KEY] = locate(
                        model.data_node_properties[self._EXPOSED_TYPE_KEY]
                    )
                elif isinstance(model.data_node_properties[self._EXPOSED_TYPE_KEY], Dict):
                    model.data_node_properties[self._EXPOSED_TYPE_KEY] = {
                        k: v if v in self._VALID_STRING_EXPOSED_TYPES else locate(v)
                        for k, v in model.data_node_properties[self._EXPOSED_TYPE_KEY].items()
                    }
                elif isinstance(model.data_node_properties[self._EXPOSED_TYPE_KEY], List):
                    model.data_node_properties[self._EXPOSED_TYPE_KEY] = [
                        v if v in self._VALID_STRING_EXPOSED_TYPES else locate(v)
                        for v in model.data_node_properties[self._EXPOSED_TYPE_KEY]
                    ]

        if self._CUSTOM_DOCUMENT_KEY in model.data_node_properties.keys():
            if isinstance(model.data_node_properties[self._CUSTOM_DOCUMENT_KEY], str):
                model.data_node_properties[self._CUSTOM_DOCUMENT_KEY] = locate(
                    model.data_node_properties[self._CUSTOM_DOCUMENT_KEY]
                )

        validity_period = None
        if model.validity_seconds is not None and model.validity_days is not None:
            validity_period = timedelta(days=model.validity_days, seconds=model.validity_seconds)
        return self.class_map[model.storage_type](
            config_id=model.config_id,
            scope=model.scope,
            id=model.id,
            name=model.name,
            owner_id=model.owner_id,
            parent_ids=set(model.parent_ids),
            last_edit_date=datetime.fromisoformat(model.last_edit_date) if model.last_edit_date else None,
            edits=model.edits,
            version=model.version,
            validity_period=validity_period,
            edit_in_progress=model.edit_in_progress,
            properties=model.data_node_properties,
        )

    def load(self, model_id: str) -> DataNode:
        return self.repo.load(model_id)

    def _load_all(self, version_number: Optional[str] = None) -> List[DataNode]:
        return self.repo._load_all(version_number)

    def _load_all_by(self, by, version_number: Optional[str] = None) -> List[DataNode]:
        return self.repo._load_all_by(by, version_number)

    def _save(self, entity: DataNode):
        return self.repo._save(entity)

    def _delete(self, entity_id: str):
        return self.repo._delete(entity_id)

    def _delete_all(self):
        return self.repo._delete_all()

    def _delete_by(self, attribute: str, value: str, version_number: Optional[str] = None):
        return self.repo._delete_by(attribute, value, version_number)

    def _delete_many(self, ids: Iterable[str]):
        return self.repo._delete_many(ids)

    def _search(self, attribute: str, value: Any, version_number: Optional[str] = None) -> Optional[DataNode]:
        return self.repo._search(attribute, value, version_number)

    def _export(self, entity_id: str, folder_path: Union[str, pathlib.Path]):
        return self.repo._export(entity_id, folder_path)
