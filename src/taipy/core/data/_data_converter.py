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

from datetime import datetime, timedelta
from pydoc import locate
from typing import Dict, List

from .._repository._v2._abstract_converter import _AbstractConverter
from .._version._utils import _migrate_entity
from ..common._utils import _load_fct
from ..data._data_model import _DataNodeModel
from ..data.data_node import DataNode
from . import GenericDataNode, JSONDataNode, SQLDataNode


class _DataNodeConverter(_AbstractConverter):
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

    @classmethod
    def _entity_to_model(cls, data_node: DataNode) -> _DataNodeModel:
        properties = data_node._properties.data.copy()
        if data_node.storage_type() == GenericDataNode.storage_type():
            read_fct = data_node._properties.get(GenericDataNode.__OPTIONAL_READ_FUNCTION_PROPERTY, None)
            properties[cls._READ_FCT_NAME_KEY] = read_fct.__name__ if read_fct else None
            properties[cls._READ_FCT_MODULE_KEY] = read_fct.__module__ if read_fct else None

            write_fct = data_node._properties.get(GenericDataNode.__OPTIONAL_WRITE_FUNCTION_PROPERTY, None)
            properties[cls._WRITE_FCT_NAME_KEY] = write_fct.__name__ if write_fct else None
            properties[cls._WRITE_FCT_MODULE_KEY] = write_fct.__module__ if write_fct else None

            del (
                properties[GenericDataNode.__OPTIONAL_READ_FUNCTION_PROPERTY],
                properties[GenericDataNode.__OPTIONAL_WRITE_FUNCTION_PROPERTY],
            )

        if data_node.storage_type() == JSONDataNode.storage_type():
            encoder = data_node._properties.get(JSONDataNode.__ENCODER_KEY)
            properties[cls._JSON_ENCODER_NAME_KEY] = encoder.__name__ if encoder else None
            properties[cls._JSON_ENCODER_MODULE_KEY] = encoder.__module__ if encoder else None
            properties.pop(JSONDataNode.__ENCODER_KEY, None)

            decoder = data_node._properties.get(JSONDataNode.__DECODER_KEY)
            properties[cls._JSON_DECODER_NAME_KEY] = decoder.__name__ if decoder else None
            properties[cls._JSON_DECODER_MODULE_KEY] = decoder.__module__ if decoder else None
            properties.pop(JSONDataNode.__DECODER_KEY, None)

        if data_node.storage_type() == SQLDataNode.storage_type():
            query_builder = data_node._properties.get(SQLDataNode.__WRITE_QUERY_BUILDER_KEY)
            properties[cls._WRITE_QUERY_BUILDER_NAME_KEY] = query_builder.__name__ if query_builder else None
            properties[cls._WRITE_QUERY_BUILDER_MODULE_KEY] = query_builder.__module__ if query_builder else None
            properties.pop(SQLDataNode.__WRITE_QUERY_BUILDER_KEY, None)

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

    @classmethod
    def _model_to_entity(cls, model: _DataNodeModel) -> DataNode:
        if model.storage_type == GenericDataNode.storage_type():
            if model.data_node_properties[cls._READ_FCT_MODULE_KEY]:
                model.data_node_properties[GenericDataNode.__OPTIONAL_READ_FUNCTION_PROPERTY] = _load_fct(
                    model.data_node_properties[cls._READ_FCT_MODULE_KEY],
                    model.data_node_properties[cls._READ_FCT_NAME_KEY],
                )
            else:
                model.data_node_properties[GenericDataNode.__OPTIONAL_READ_FUNCTION_PROPERTY] = None

            if model.data_node_properties[cls._WRITE_FCT_MODULE_KEY]:
                model.data_node_properties[GenericDataNode.__OPTIONAL_WRITE_FUNCTION_PROPERTY] = _load_fct(
                    model.data_node_properties[cls._WRITE_FCT_MODULE_KEY],
                    model.data_node_properties[cls._WRITE_FCT_NAME_KEY],
                )
            else:
                model.data_node_properties[GenericDataNode.__OPTIONAL_WRITE_FUNCTION_PROPERTY] = None

            del model.data_node_properties[cls._READ_FCT_NAME_KEY]
            del model.data_node_properties[cls._READ_FCT_MODULE_KEY]
            del model.data_node_properties[cls._WRITE_FCT_NAME_KEY]
            del model.data_node_properties[cls._WRITE_FCT_MODULE_KEY]

        if model.storage_type == JSONDataNode.storage_type():
            if model.data_node_properties[cls._JSON_ENCODER_MODULE_KEY]:
                model.data_node_properties[JSONDataNode.__ENCODER_KEY] = _load_fct(
                    model.data_node_properties[cls._JSON_ENCODER_MODULE_KEY],
                    model.data_node_properties[cls._JSON_ENCODER_NAME_KEY],
                )
            else:
                model.data_node_properties[JSONDataNode.__ENCODER_KEY] = None

            if model.data_node_properties[cls._JSON_DECODER_MODULE_KEY]:
                model.data_node_properties[JSONDataNode.__DECODER_KEY] = _load_fct(
                    model.data_node_properties[cls._JSON_DECODER_MODULE_KEY],
                    model.data_node_properties[cls._JSON_DECODER_NAME_KEY],
                )
            else:
                model.data_node_properties[JSONDataNode.__DECODER_KEY] = None

            del model.data_node_properties[cls._JSON_ENCODER_NAME_KEY]
            del model.data_node_properties[cls._JSON_ENCODER_MODULE_KEY]
            del model.data_node_properties[cls._JSON_DECODER_NAME_KEY]
            del model.data_node_properties[cls._JSON_DECODER_MODULE_KEY]

        if model.storage_type == SQLDataNode.storage_type():
            if model.data_node_properties[cls._WRITE_QUERY_BUILDER_MODULE_KEY]:
                model.data_node_properties[SQLDataNode.__WRITE_QUERY_BUILDER_KEY] = _load_fct(
                    model.data_node_properties[cls._WRITE_QUERY_BUILDER_MODULE_KEY],
                    model.data_node_properties[cls._WRITE_QUERY_BUILDER_NAME_KEY],
                )
            else:
                model.data_node_properties[SQLDataNode.__WRITE_QUERY_BUILDER_KEY] = None

            del model.data_node_properties[cls._WRITE_QUERY_BUILDER_NAME_KEY]
            del model.data_node_properties[cls._WRITE_QUERY_BUILDER_MODULE_KEY]

        if cls._EXPOSED_TYPE_KEY in model.data_node_properties.keys():
            if model.data_node_properties[cls._EXPOSED_TYPE_KEY] not in cls._VALID_STRING_EXPOSED_TYPES:
                if isinstance(model.data_node_properties[cls._EXPOSED_TYPE_KEY], str):
                    model.data_node_properties[cls._EXPOSED_TYPE_KEY] = locate(
                        model.data_node_properties[cls._EXPOSED_TYPE_KEY]
                    )
                elif isinstance(model.data_node_properties[cls._EXPOSED_TYPE_KEY], Dict):
                    model.data_node_properties[cls._EXPOSED_TYPE_KEY] = {
                        k: v if v in cls._VALID_STRING_EXPOSED_TYPES else locate(v)
                        for k, v in model.data_node_properties[cls._EXPOSED_TYPE_KEY].items()
                    }
                elif isinstance(model.data_node_properties[cls._EXPOSED_TYPE_KEY], List):
                    model.data_node_properties[cls._EXPOSED_TYPE_KEY] = [
                        v if v in cls._VALID_STRING_EXPOSED_TYPES else locate(v)
                        for v in model.data_node_properties[cls._EXPOSED_TYPE_KEY]
                    ]

        if cls._CUSTOM_DOCUMENT_KEY in model.data_node_properties.keys():
            if isinstance(model.data_node_properties[cls._CUSTOM_DOCUMENT_KEY], str):
                model.data_node_properties[cls._CUSTOM_DOCUMENT_KEY] = locate(
                    model.data_node_properties[cls._CUSTOM_DOCUMENT_KEY]
                )

        validity_period = None
        if model.validity_seconds is not None and model.validity_days is not None:
            validity_period = timedelta(days=model.validity_days, seconds=model.validity_seconds)

        datanode = DataNode._class_map()[model.storage_type](
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
        return _migrate_entity(datanode)
