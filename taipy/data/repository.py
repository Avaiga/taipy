import pathlib
from datetime import datetime

from taipy.config.config import Config
from taipy.data import DataNode
from taipy.data.data_node_model import DataNodeModel
from taipy.repository import FileSystemRepository


class DataRepository(FileSystemRepository[DataNodeModel, DataNode]):
    def __init__(self, class_map):
        super().__init__(model=DataNodeModel, dir_name="data_nodes")
        self.class_map = class_map

    def to_model(self, data_node: DataNode):
        return DataNodeModel(
            data_node.id,
            data_node.config_name,
            data_node.scope,
            data_node.storage_type(),
            data_node.name,
            data_node.parent_id,
            data_node.last_edition_date.isoformat() if data_node.last_edition_date else None,
            data_node.job_ids,
            data_node.validity_days,
            data_node.validity_hours,
            data_node.validity_minutes,
            data_node.edition_in_progress,
            data_node.properties,
        )

    def from_model(self, model: DataNodeModel):
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
