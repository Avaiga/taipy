from datetime import datetime

from taipy.data import DataSource
from taipy.data.data_source_model import DataSourceModel
from taipy.repository import FileSystemRepository


class DataRepository(FileSystemRepository[DataSourceModel, DataSource]):
    def __init__(self, class_map, dir_name="data_sources"):
        super().__init__(
            model=DataSourceModel,
            dir_name=dir_name,
        )
        self.class_map = class_map

    def to_model(self, data_source: DataSource):
        return DataSourceModel(
            data_source.id,
            data_source.config_name,
            data_source.scope,
            data_source.type(),
            data_source.name,
            data_source.parent_id,
            data_source.last_edition_date.isoformat() if data_source.last_edition_date else None,
            data_source.job_ids,
            data_source.up_to_date,
            data_source.properties,
        )

    def from_model(self, model: DataSourceModel):
        return self.class_map[model.type](
            config_name=model.config_name,
            scope=model.scope,
            id=model.id,
            name=model.name,
            parent_id=model.parent_id,
            last_edition_date=datetime.fromisoformat(model.last_edition_date) if model.last_edition_date else None,
            job_ids=model.job_ids,
            up_to_date=model.up_to_date,
            properties=model.data_source_properties,
        )
