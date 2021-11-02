from taipy.data.data_source_model import DataSourceModel
from taipy.repository import FileSystemRepository


class DataRepository(FileSystemRepository[DataSourceModel]):
    def __init__(self, class_map, dir_name="data_sources"):
        super().__init__(
            model=DataSourceModel,
            dir_name=dir_name,
        )
        self.class_map = class_map

    def to_model(self, data_source):
        return DataSourceModel(
            data_source.id,
            data_source.config_name,
            data_source.scope,
            data_source.type(),
            data_source.parent_id,
            data_source.properties,
        )

    def from_model(self, model):
        return self.class_map[model.type](
            config_name=model.config_name,
            scope=model.scope,
            id=model.id,
            parent_id=model.parent_id,
            properties=model.data_source_properties,
        )
