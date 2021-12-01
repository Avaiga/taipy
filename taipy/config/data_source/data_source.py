from taipy.common import protect_name
from taipy.config.data_source import DataSourceSerializer
from taipy.config.interface import ConfigRepository
from taipy.data.scope import Scope


class DataSourceConfig:
    """
    Contains the Configuration of a datasource by mixing arguments with globals Configurations
    """

    def __init__(self, name: str, storage_type: str = "pickle", scope=Scope.PIPELINE, **kwargs):
        self.name = protect_name(name)
        self.storage_type = storage_type
        self.scope = scope
        self.properties = kwargs


class DataSourceConfigs(ConfigRepository):
    def __init__(self, config: DataSourceSerializer):
        super().__init__()
        self.__config = config

    def create(self, name: str, storage_type: str, scope=Scope.PIPELINE, **kwargs):  # type: ignore
        kwargs = {**kwargs, **self.__config[name]}  # type: ignore
        data_source_config = DataSourceConfig(name, storage_type, scope, **kwargs)
        self._data[name] = data_source_config
        return data_source_config
