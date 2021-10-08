from taipy.configuration import ConfigurationManager
from taipy.configuration.data_manager_configuration import DataManagerConfiguration
from taipy.data.scope import Scope


class DataSourceConfig:
    """
    Contains the Configuration of a datasource by mixing arguments with globals Configurations
    """

    def __init__(self, name: str, type: str, scope=Scope.PIPELINE, **kwargs):
        self.name = name.strip().lower().replace(" ", "_")
        self.type = type
        self.scope = scope
        self.properties = kwargs

    def __and__(self, config: DataManagerConfiguration):
        _config = config[self.name] or {}
        properties = {**self.properties, **_config}
        return DataSourceConfig(name=self.name, type=self.type, scope=self.scope, **properties)
