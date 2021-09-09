from typing import Dict, Optional

from taipy.exceptions import MissingRequiredProperty

from .data_source_entity import DataSourceEntity


class EmbeddedDataSourceEntity(DataSourceEntity):
    __REQUIRED_PROPERTIES = ["data"]

    def __init__(self, name: str, scope: int, id: Optional[str], properties):
        if missing := set(self.__REQUIRED_PROPERTIES) - set(properties.keys()):
            raise MissingRequiredProperty(
                f"The following properties {','.join(x for x in missing)} were not informed and are required"
            )
        super().__init__(name, scope, data=properties.get("data"))

    @classmethod
    def create(cls, name: str, scope: int, id: str, data: Dict):
        return EmbeddedDataSourceEntity(name, scope, id, {"data": data})

    def preview(self):
        print(f"{self.properties.get('data')}", flush=True)

    def get(self, query):
        """
        Temporary function interface, will be remove
        """
        return self.properties.get('data')

    def write(self, data):
        """
        Temporary function interface, will be remove
        """
        self.properties['data'] = data
