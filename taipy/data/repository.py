from taipy.repository import FileSystemStorage

from .data_source_model import DataSourceModel


class DataRepository(FileSystemStorage[DataSourceModel]):
    pass


repository = DataRepository(DataSourceModel, dir_name=".data")
