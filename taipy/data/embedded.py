import json
from typing import Any, Dict, Optional

from taipy.data.data_source import DataSource
from taipy.data.scope import Scope


class EmbeddedDataSource(DataSource):
    __TYPE = "embedded"

    def __init__(
        self, config_name: str, scope: Scope, id: Optional[str] = None, properties: Dict = {}
    ):
        super().__init__(config_name, scope, id, data=properties.get("data"))

    @classmethod
    def create(cls, config_name: str, scope: Scope, data: Any):
        return EmbeddedDataSource(config_name, scope, None, {"data": data})

    @classmethod
    def type(cls) -> str:
        return cls.__TYPE

    def preview(self):
        print(f"{self.properties.get('data')}", flush=True)

    def get(self, query=None):
        """
        Temporary function interface, will be remove
        """
        return self.properties.get("data")

    def write(self, data):
        """
        Temporary function interface, will be remove
        """
        self.properties["data"] = data

    def to_json(self):
        return json.dumps(
            {
                "config_name": self.config_name,
                "type": "embedded",
                "scope": self.scope.name,
                "data": self.data,
            }
        )

    @staticmethod
    def from_json(data_source_dict):
        return EmbeddedDataSource.create(
            config_name=data_source_dict.get("config_name"),
            scope=Scope[data_source_dict.get("scope")],
            data=data_source_dict.get("data"),
        )
