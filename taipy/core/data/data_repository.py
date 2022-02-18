import pathlib
from copy import copy
from datetime import datetime

from taipy.core.common.utils import load_fct
from taipy.core.config.config import Config
from taipy.core.data.data_model import DataNodeModel
from taipy.core.data.data_node import DataNode
from taipy.core.data.generic import GenericDataNode
from taipy.core.repository import FileSystemRepository


class DataRepository(FileSystemRepository[DataNodeModel, DataNode]):
    READ_FCT_NAME_KEY = "read_fct_name"
    READ_FCT_MODULE_KEY = "read_fct_module"
    WRITE_FCT_NAME_KEY = "write_fct_name"
    WRITE_FCT_MODULE_KEY = "write_fct_module"

    def __init__(self, class_map):
        super().__init__(model=DataNodeModel, dir_name="data_nodes")
        self.class_map = class_map

    def to_model(self, data_node: DataNode):
        properties = data_node._properties.data.copy()
        if data_node.storage_type() == GenericDataNode.storage_type():
            properties[self.READ_FCT_NAME_KEY] = data_node._properties[
                GenericDataNode._REQUIRED_READ_FUNCTION_PROPERTY
            ].__name__
            properties[self.READ_FCT_MODULE_KEY] = data_node._properties[
                GenericDataNode._REQUIRED_READ_FUNCTION_PROPERTY
            ].__module__
            properties[self.WRITE_FCT_NAME_KEY] = data_node._properties[
                GenericDataNode._REQUIRED_WRITE_FUNCTION_PROPERTY
            ].__name__
            properties[self.WRITE_FCT_MODULE_KEY] = data_node._properties[
                GenericDataNode._REQUIRED_WRITE_FUNCTION_PROPERTY
            ].__module__
            del (
                properties[GenericDataNode._REQUIRED_READ_FUNCTION_PROPERTY],
                properties[GenericDataNode._REQUIRED_WRITE_FUNCTION_PROPERTY],
            )

        return DataNodeModel(
            data_node.id,
            data_node.config_name,
            data_node.scope,
            data_node.storage_type(),
            data_node._name,
            data_node.parent_id,
            data_node._last_edition_date.isoformat() if data_node._last_edition_date else None,
            data_node._job_ids,
            data_node._validity_days,
            data_node._validity_hours,
            data_node._validity_minutes,
            data_node._edition_in_progress,
            properties,
        )

    def from_model(self, model: DataNodeModel):
        if model.storage_type == GenericDataNode.storage_type():
            model.data_node_properties[GenericDataNode._REQUIRED_READ_FUNCTION_PROPERTY] = load_fct(
                model.data_node_properties[self.READ_FCT_MODULE_KEY], model.data_node_properties[self.READ_FCT_NAME_KEY]
            )
            model.data_node_properties[GenericDataNode._REQUIRED_WRITE_FUNCTION_PROPERTY] = load_fct(
                model.data_node_properties[self.WRITE_FCT_MODULE_KEY],
                model.data_node_properties[self.WRITE_FCT_NAME_KEY],
            )
            del model.data_node_properties[self.READ_FCT_NAME_KEY]
            del model.data_node_properties[self.READ_FCT_MODULE_KEY]
            del model.data_node_properties[self.WRITE_FCT_NAME_KEY]
            del model.data_node_properties[self.WRITE_FCT_MODULE_KEY]
        return self.class_map[model.storage_type](
            config_name=model.config_name,
            scope=model.scope,
            id=model.id,
            name=model.name,
            parent_id=model.parent_id,
            last_edition_date=datetime.fromisoformat(model.last_edition_date) if model.last_edition_date else None,
            job_ids=model.job_ids,
            validity_days=model.validity_days,
            validity_hours=model.validity_hours,
            validity_minutes=model.validity_minutes,
            edition_in_progress=model.edition_in_progress,
            properties=model.data_node_properties,
        )

    @property
    def storage_folder(self) -> pathlib.Path:
        return pathlib.Path(Config.global_config().storage_folder)  # type: ignore
