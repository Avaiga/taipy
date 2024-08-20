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

from copy import copy
from datetime import datetime, timedelta
from pydoc import locate

from .._repository._abstract_converter import _AbstractConverter
from ..common._utils import _load_fct
from ..data._data_model import _DataNodeModel
from ..data.data_node import DataNode
from . import GenericDataNode, JSONDataNode, MongoCollectionDataNode, SQLDataNode


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
    __WRITE_QUERY_BUILDER_NAME_KEY = "write_query_builder_name"
    __WRITE_QUERY_BUILDER_MODULE_KEY = "write_query_builder_module"
    __APPEND_QUERY_BUILDER_NAME_KEY = "append_query_builder_name"
    __APPEND_QUERY_BUILDER_MODULE_KEY = "append_query_builder_module"
    # TODO: This limits the valid string to only the ones provided by the Converter.
    # While in practice, each data nodes might have different exposed type possibilities.
    # The previous implementation used tabular datanode but it's no longer suitable so
    # new proposal is needed.
    _VALID_STRING_EXPOSED_TYPES = ["numpy", "pandas", "modin"]  # Modin is deprecated in favor of pandas since 3.1.0

    @classmethod
    def __serialize_generic_dn_properties(cls, datanode_properties: dict):
        read_fct = datanode_properties.get(GenericDataNode._OPTIONAL_READ_FUNCTION_PROPERTY, None)
        datanode_properties[cls._READ_FCT_NAME_KEY] = read_fct.__name__ if read_fct else None
        datanode_properties[cls._READ_FCT_MODULE_KEY] = read_fct.__module__ if read_fct else None

        write_fct = datanode_properties.get(GenericDataNode._OPTIONAL_WRITE_FUNCTION_PROPERTY, None)
        datanode_properties[cls._WRITE_FCT_NAME_KEY] = write_fct.__name__ if write_fct else None
        datanode_properties[cls._WRITE_FCT_MODULE_KEY] = write_fct.__module__ if write_fct else None

        del (
            datanode_properties[GenericDataNode._OPTIONAL_READ_FUNCTION_PROPERTY],
            datanode_properties[GenericDataNode._OPTIONAL_WRITE_FUNCTION_PROPERTY],
        )
        return datanode_properties

    @classmethod
    def __serialize_json_dn_properties(cls, datanode_properties: dict):
        encoder = datanode_properties.get(JSONDataNode._ENCODER_KEY)
        datanode_properties[cls._JSON_ENCODER_NAME_KEY] = encoder.__name__ if encoder else None
        datanode_properties[cls._JSON_ENCODER_MODULE_KEY] = encoder.__module__ if encoder else None
        datanode_properties.pop(JSONDataNode._ENCODER_KEY, None)

        decoder = datanode_properties.get(JSONDataNode._DECODER_KEY)
        datanode_properties[cls._JSON_DECODER_NAME_KEY] = decoder.__name__ if decoder else None
        datanode_properties[cls._JSON_DECODER_MODULE_KEY] = decoder.__module__ if decoder else None
        datanode_properties.pop(JSONDataNode._DECODER_KEY, None)

        return datanode_properties

    @classmethod
    def __serialize_sql_dn_properties(cls, datanode_properties: dict) -> dict:
        write_qb = datanode_properties.get(SQLDataNode._WRITE_QUERY_BUILDER_KEY)
        datanode_properties[cls.__WRITE_QUERY_BUILDER_NAME_KEY] = write_qb.__name__ if write_qb else None
        datanode_properties[cls.__WRITE_QUERY_BUILDER_MODULE_KEY] = write_qb.__module__ if write_qb else None
        datanode_properties.pop(SQLDataNode._WRITE_QUERY_BUILDER_KEY, None)

        append_qb = datanode_properties.get(SQLDataNode._APPEND_QUERY_BUILDER_KEY)
        datanode_properties[cls.__APPEND_QUERY_BUILDER_NAME_KEY] = append_qb.__name__ if append_qb else None
        datanode_properties[cls.__APPEND_QUERY_BUILDER_MODULE_KEY] = append_qb.__module__ if append_qb else None
        datanode_properties.pop(SQLDataNode._APPEND_QUERY_BUILDER_KEY, None)

        return datanode_properties

    @classmethod
    def __serialize_mongo_collection_dn_model_properties(cls, datanode_properties: dict) -> dict:
        if MongoCollectionDataNode._CUSTOM_DOCUMENT_PROPERTY in datanode_properties.keys():
            datanode_properties[MongoCollectionDataNode._CUSTOM_DOCUMENT_PROPERTY] = (
                f"{datanode_properties[MongoCollectionDataNode._CUSTOM_DOCUMENT_PROPERTY].__module__}."
                f"{datanode_properties[MongoCollectionDataNode._CUSTOM_DOCUMENT_PROPERTY].__qualname__}"
            )

        return datanode_properties

    @classmethod
    def __serialize_edits(cls, edits):
        new_edits = []
        for edit in edits:
            new_edit = edit.copy()
            if timestamp := new_edit.get("timestamp", None):
                new_edit["timestamp"] = timestamp.isoformat()
            else:
                new_edit["timestamp"] = datetime.now().isoformat()
            new_edits.append(new_edit)
        return new_edits

    @staticmethod
    def __serialize_exposed_type(properties: dict, exposed_type_key: str, valid_str_exposed_types) -> dict:
        if not isinstance(properties[exposed_type_key], str):
            if isinstance(properties[exposed_type_key], dict):
                properties[exposed_type_key] = {
                    k: v if v in valid_str_exposed_types else f"{v.__module__}.{v.__qualname__}"
                    for k, v in properties[exposed_type_key].items()
                }
            elif isinstance(properties[exposed_type_key], list):
                properties[exposed_type_key] = [
                    v if v in valid_str_exposed_types else f"{v.__module__}.{v.__qualname__}"
                    for v in properties[exposed_type_key]
                ]
            else:
                properties[
                    exposed_type_key
                ] = f"{properties[exposed_type_key].__module__}.{properties[exposed_type_key].__qualname__}"
        return properties

    @classmethod
    def _entity_to_model(cls, data_node: DataNode) -> _DataNodeModel:
        properties = data_node._properties.data.copy()
        if data_node.storage_type() == GenericDataNode.storage_type():
            properties = cls.__serialize_generic_dn_properties(properties)

        if data_node.storage_type() == JSONDataNode.storage_type():
            properties = cls.__serialize_json_dn_properties(properties)

        if data_node.storage_type() == SQLDataNode.storage_type():
            properties = cls.__serialize_sql_dn_properties(properties)

        if data_node.storage_type() == MongoCollectionDataNode.storage_type():
            properties = cls.__serialize_mongo_collection_dn_model_properties(properties)

        if cls._EXPOSED_TYPE_KEY in properties.keys():
            properties = cls.__serialize_exposed_type(
                properties, cls._EXPOSED_TYPE_KEY, cls._VALID_STRING_EXPOSED_TYPES
            )

        return _DataNodeModel(
            data_node.id,
            data_node.config_id,
            data_node._scope,
            data_node.storage_type(),
            data_node.owner_id,
            list(data_node._parent_ids),
            data_node._last_edit_date.isoformat() if data_node._last_edit_date else None,
            cls.__serialize_edits(data_node._edits),
            data_node._version,
            data_node._validity_period.days if data_node._validity_period else None,
            data_node._validity_period.seconds if data_node._validity_period else None,
            data_node._edit_in_progress,
            data_node._editor_id,
            data_node._editor_expiration_date.isoformat() if data_node._editor_expiration_date else None,
            properties,
        )

    @classmethod
    def __deserialize_generic_dn_properties(cls, datanode_model_properties):
        if datanode_model_properties[cls._READ_FCT_MODULE_KEY]:
            datanode_model_properties[GenericDataNode._OPTIONAL_READ_FUNCTION_PROPERTY] = _load_fct(
                datanode_model_properties[cls._READ_FCT_MODULE_KEY],
                datanode_model_properties[cls._READ_FCT_NAME_KEY],
            )
        else:
            datanode_model_properties[GenericDataNode._OPTIONAL_READ_FUNCTION_PROPERTY] = None

        if datanode_model_properties[cls._WRITE_FCT_MODULE_KEY]:
            datanode_model_properties[GenericDataNode._OPTIONAL_WRITE_FUNCTION_PROPERTY] = _load_fct(
                datanode_model_properties[cls._WRITE_FCT_MODULE_KEY],
                datanode_model_properties[cls._WRITE_FCT_NAME_KEY],
            )
        else:
            datanode_model_properties[GenericDataNode._OPTIONAL_WRITE_FUNCTION_PROPERTY] = None

        del datanode_model_properties[cls._READ_FCT_NAME_KEY]
        del datanode_model_properties[cls._READ_FCT_MODULE_KEY]
        del datanode_model_properties[cls._WRITE_FCT_NAME_KEY]
        del datanode_model_properties[cls._WRITE_FCT_MODULE_KEY]

        return datanode_model_properties

    @classmethod
    def __deserialize_json_dn_properties(cls, datanode_model_properties: dict) -> dict:
        if datanode_model_properties[cls._JSON_ENCODER_MODULE_KEY]:
            datanode_model_properties[JSONDataNode._ENCODER_KEY] = _load_fct(
                datanode_model_properties[cls._JSON_ENCODER_MODULE_KEY],
                datanode_model_properties[cls._JSON_ENCODER_NAME_KEY],
            )
        else:
            datanode_model_properties[JSONDataNode._ENCODER_KEY] = None

        if datanode_model_properties[cls._JSON_DECODER_MODULE_KEY]:
            datanode_model_properties[JSONDataNode._DECODER_KEY] = _load_fct(
                datanode_model_properties[cls._JSON_DECODER_MODULE_KEY],
                datanode_model_properties[cls._JSON_DECODER_NAME_KEY],
            )
        else:
            datanode_model_properties[JSONDataNode._DECODER_KEY] = None

        del datanode_model_properties[cls._JSON_ENCODER_NAME_KEY]
        del datanode_model_properties[cls._JSON_ENCODER_MODULE_KEY]
        del datanode_model_properties[cls._JSON_DECODER_NAME_KEY]
        del datanode_model_properties[cls._JSON_DECODER_MODULE_KEY]

        return datanode_model_properties

    @classmethod
    def __deserialize_sql_dn_model_properties(cls, datanode_model_properties: dict) -> dict:
        if datanode_model_properties[cls.__WRITE_QUERY_BUILDER_MODULE_KEY]:
            datanode_model_properties[SQLDataNode._WRITE_QUERY_BUILDER_KEY] = _load_fct(
                datanode_model_properties[cls.__WRITE_QUERY_BUILDER_MODULE_KEY],
                datanode_model_properties[cls.__WRITE_QUERY_BUILDER_NAME_KEY],
            )
        else:
            datanode_model_properties[SQLDataNode._WRITE_QUERY_BUILDER_KEY] = None

        del datanode_model_properties[cls.__WRITE_QUERY_BUILDER_NAME_KEY]
        del datanode_model_properties[cls.__WRITE_QUERY_BUILDER_MODULE_KEY]

        if datanode_model_properties[cls.__APPEND_QUERY_BUILDER_MODULE_KEY]:
            datanode_model_properties[SQLDataNode._APPEND_QUERY_BUILDER_KEY] = _load_fct(
                datanode_model_properties[cls.__APPEND_QUERY_BUILDER_MODULE_KEY],
                datanode_model_properties[cls.__APPEND_QUERY_BUILDER_NAME_KEY],
            )
        else:
            datanode_model_properties[SQLDataNode._APPEND_QUERY_BUILDER_KEY] = None

        del datanode_model_properties[cls.__APPEND_QUERY_BUILDER_NAME_KEY]
        del datanode_model_properties[cls.__APPEND_QUERY_BUILDER_MODULE_KEY]

        return datanode_model_properties

    @classmethod
    def __deserialize_mongo_collection_dn_model_properties(cls, datanode_model_properties: dict) -> dict:
        if MongoCollectionDataNode._CUSTOM_DOCUMENT_PROPERTY in datanode_model_properties.keys():
            if isinstance(datanode_model_properties[MongoCollectionDataNode._CUSTOM_DOCUMENT_PROPERTY], str):
                datanode_model_properties[MongoCollectionDataNode._CUSTOM_DOCUMENT_PROPERTY] = locate(
                    datanode_model_properties[MongoCollectionDataNode._CUSTOM_DOCUMENT_PROPERTY]
                )
        return datanode_model_properties

    @classmethod
    def __deserialize_edits(cls, edits):
        for edit in edits:
            if timestamp := edit.get("timestamp", None):
                edit["timestamp"] = datetime.fromisoformat(timestamp)
            else:
                edit["timestamp"] = datetime.now()
        return edits

    @staticmethod
    def __deserialize_exposed_type(properties: dict, exposed_type_key: str, valid_str_exposed_types) -> dict:
        if properties[exposed_type_key] not in valid_str_exposed_types:
            if isinstance(properties[exposed_type_key], str):
                properties[exposed_type_key] = locate(properties[exposed_type_key])
            elif isinstance(properties[exposed_type_key], dict):
                properties[exposed_type_key] = {
                    k: v if v in valid_str_exposed_types else locate(v) for k, v in properties[exposed_type_key].items()
                }
            elif isinstance(properties[exposed_type_key], list):
                properties[exposed_type_key] = [
                    v if v in valid_str_exposed_types else locate(v) for v in properties[exposed_type_key]
                ]
        return properties

    @classmethod
    def _model_to_entity(cls, model: _DataNodeModel) -> DataNode:
        data_node_properties = model.data_node_properties.copy()

        if model.storage_type == GenericDataNode.storage_type():
            data_node_properties = cls.__deserialize_generic_dn_properties(data_node_properties)

        if model.storage_type == JSONDataNode.storage_type():
            data_node_properties = cls.__deserialize_json_dn_properties(data_node_properties)

        if model.storage_type == SQLDataNode.storage_type():
            data_node_properties = cls.__deserialize_sql_dn_model_properties(data_node_properties)

        if model.storage_type == MongoCollectionDataNode.storage_type():
            data_node_properties = cls.__deserialize_mongo_collection_dn_model_properties(data_node_properties)

        if cls._EXPOSED_TYPE_KEY in data_node_properties.keys():
            data_node_properties = cls.__deserialize_exposed_type(
                data_node_properties, cls._EXPOSED_TYPE_KEY, cls._VALID_STRING_EXPOSED_TYPES
            )

        validity_period = None
        if model.validity_seconds is not None and model.validity_days is not None:
            validity_period = timedelta(days=model.validity_days, seconds=model.validity_seconds)

        exp_date = datetime.fromisoformat(model.editor_expiration_date) if model.editor_expiration_date else None
        return DataNode._class_map()[model.storage_type](
            config_id=model.config_id,
            scope=model.scope,
            id=model.id,
            owner_id=model.owner_id,
            parent_ids=set(model.parent_ids),
            last_edit_date=datetime.fromisoformat(model.last_edit_date) if model.last_edit_date else None,
            edits=cls.__deserialize_edits(copy(model.edits)),
            version=model.version,
            validity_period=validity_period,
            edit_in_progress=model.edit_in_progress,
            editor_id=model.editor_id,
            editor_expiration_date=exp_date,
            properties=data_node_properties,
        )
