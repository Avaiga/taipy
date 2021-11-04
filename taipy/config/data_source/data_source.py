import re
import unidecode
from taipy.config.data_source import DataSourceSerializer
from taipy.config.interface import ConfigRepository
from taipy.data.scope import Scope


class DataSourceConfig:
    """
    Contains the Configuration of a datasource by mixing arguments with globals Configurations
    """

    def __init__(self, name: str, type: str, scope=Scope.PIPELINE, **kwargs):
        self.name = re.sub(r'[\W]+', '-', unidecode.unidecode(name).strip().lower().replace(' ', '_'))
        self.type = type
        self.scope = scope
        self.properties = kwargs


class DataSourceConfigs(ConfigRepository):
    def __init__(self, config: DataSourceSerializer):
        super().__init__()
        self.__config = config

    def create(self, name: str, type: str, scope=Scope.PIPELINE, **kwargs):  # type: ignore
        kwargs = {**kwargs, **self.__config[name]}  # type: ignore
        data_source_config = DataSourceConfig(name, type, scope, **kwargs)
        self._data[name] = data_source_config
        return data_source_config
