from taipy.data.data_source_model import DataSourceModel
from taipy.repository import FileSystemRepository


class DataRepository(FileSystemRepository[DataSourceModel]):
    pass
