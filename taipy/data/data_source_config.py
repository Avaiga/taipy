from taipy.data.scope import Scope


class DataSourceConfig:
    def __init__(self, name: str, type: str, scope=Scope.PIPELINE, **kwargs):
        self.type = type
        self.name = name.strip().lower().replace(' ', '_')
        self.scope = scope
        self.properties = kwargs
