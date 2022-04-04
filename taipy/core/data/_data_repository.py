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

import pathlib
from datetime import datetime, timedelta
from pydoc import locate
from typing import Dict

from taipy.core._repository import _FileSystemRepository
from taipy.core.common._utils import _load_fct
from taipy.core.config.config import Config
from taipy.core.data._data_model import _DataNodeModel
from taipy.core.data.data_node import DataNode
from taipy.core.data.generic import GenericDataNode


class _DataRepository(_FileSystemRepository[_DataNodeModel, DataNode]):
    _READ_FCT_NAME_KEY = "read_fct_name"
    _READ_FCT_MODULE_KEY = "read_fct_module"
    _WRITE_FCT_NAME_KEY = "write_fct_name"
    _WRITE_FCT_MODULE_KEY = "write_fct_module"
    _EXPOSED_TYPE_KEY = "exposed_type"

    def __init__(self, class_map):
        super().__init__(model=_DataNodeModel, dir_name="data_nodes")
        self.class_map = class_map

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

        if self._EXPOSED_TYPE_KEY in properties.keys():
            if not isinstance(properties[self._EXPOSED_TYPE_KEY], str):
                if isinstance(properties[self._EXPOSED_TYPE_KEY], Dict):
                    properties[self._EXPOSED_TYPE_KEY] = {
                        k: f"{v.__module__}.{v.__qualname__}" for k, v in properties[self._EXPOSED_TYPE_KEY].items()
                    }
                else:
                    properties[
                        self._EXPOSED_TYPE_KEY
                    ] = f"{properties[self._EXPOSED_TYPE_KEY].__module__}.{properties[self._EXPOSED_TYPE_KEY].__qualname__}"

        return _DataNodeModel(
            data_node.id,
            data_node.config_id,
            data_node._scope,
            data_node.storage_type(),
            data_node._name,
            data_node.parent_id,
            data_node._last_edition_date.isoformat() if data_node._last_edition_date else None,
            data_node._job_ids.data,
            data_node._validity_period.days if data_node._validity_period else None,
            data_node._validity_period.seconds if data_node._validity_period else None,
            data_node._edition_in_progress,
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

        if self._EXPOSED_TYPE_KEY in model.data_node_properties.keys():
            if model.data_node_properties[self._EXPOSED_TYPE_KEY] != "numpy":
                if isinstance(model.data_node_properties[self._EXPOSED_TYPE_KEY], str):
                    model.data_node_properties[self._EXPOSED_TYPE_KEY] = locate(
                        model.data_node_properties[self._EXPOSED_TYPE_KEY]
                    )
                if isinstance(model.data_node_properties[self._EXPOSED_TYPE_KEY], Dict):
                    model.data_node_properties[self._EXPOSED_TYPE_KEY] = {
                        k: locate(v) for k, v in model.data_node_properties[self._EXPOSED_TYPE_KEY].items()
                    }

        validity_period = None
        if model.validity_seconds is not None and model.validity_days is not None:
            validity_period = timedelta(days=model.validity_days, seconds=model.validity_seconds)
        return self.class_map[model.storage_type](
            config_id=model.config_id,
            scope=model.scope,
            id=model.id,
            name=model.name,
            parent_id=model.parent_id,
            last_edition_date=datetime.fromisoformat(model.last_edition_date) if model.last_edition_date else None,
            job_ids=model.job_ids,
            validity_period=validity_period,
            edition_in_progress=model.edition_in_progress,
            properties=model.data_node_properties,
        )

    @property
    def _storage_folder(self) -> pathlib.Path:
        return pathlib.Path(Config.global_config.storage_folder)  # type: ignore
