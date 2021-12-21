from datetime import datetime

from taipy.config.config import Config
from taipy.data import DataSource
from taipy.data.data_source_model import DataSourceModel
from taipy.repository import FileSystemRepository


class DataRepository(FileSystemRepository[DataSourceModel, DataSource]):
    def __init__(self, class_map, dir_name="data_sources", base_path=Config.global_config().storage_folder):
        super().__init__(model=DataSourceModel, dir_name=dir_name, base_path=base_path)
        self.class_map = class_map

    def to_model(self, data_source: DataSource):
        return DataSourceModel(
            data_source.id,
            data_source.config_name,
            data_source.scope,
            data_source.storage_type(),
            data_source.name,
            data_source.parent_id,
            data_source.last_edition_date.isoformat() if data_source.last_edition_date else None,
            data_source.job_ids,
            data_source.validity_days,
            data_source.validity_hours,
            data_source.validity_minutes,
            data_source.edition_in_progress,
            data_source.properties,
        )

    def from_model(self, model: DataSourceModel):
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
            properties=model.data_source_properties,
        )
