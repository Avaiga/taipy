import json
from typing import Any, Dict, List, Optional

import pandas as pd

from taipy.data.data_source_entity import DataSourceEntity
from taipy.data.scope import Scope
from taipy.exceptions import MissingRequiredProperty


class CSVDataSourceEntity(DataSourceEntity):
    """
    A class to represent a CSV Data Source.

    Attributes
    ----------
    name: str
        name that identifies the data entity
    scope: int
        number that refers to the scope of usage of the data entity
    properties: list
        list of additional arguments
    """

    __REQUIRED_PROPERTIES = ["path", "has_header"]
    __TYPE = "csv"

    def __init__(
        self, name: str, scope: Scope, id: Optional[str] = None, properties: Dict = {}
    ):
        if missing := set(self.__REQUIRED_PROPERTIES) - set(properties.keys()):
            raise MissingRequiredProperty(
                f"The following properties "
                f"{', '.join(x for x in missing)} were not informed and are required"
            )
        super().__init__(
            name,
            scope,
            id,
            path=properties.get("path"),
            has_header=properties.get("has_header"),
        )

    @classmethod
    def create(
        cls,
        name: str,
        scope: Scope,
        path: str,
        has_header: bool = False,
    ) -> DataSourceEntity:
        return CSVDataSourceEntity(
            name, scope, None, {"path": path, "has_header": has_header}
        )

    @classmethod
    def type(cls) -> str:
        return cls.__TYPE

    def preview(self):
        df = pd.read_csv(self.path)
        print(df.head())

    def get(self, query=None):
        return pd.read_csv(self.properties["path"])

    def write(self, data: Any, columns: List[str] = []):
        if not columns:
            df = pd.DataFrame(data)
        else:
            df = pd.DataFrame(data, columns=columns)
        df.to_csv(self.path, index=False)

    def to_json(self):
        return json.dumps(
            {
                "name": self.name,
                "type": "csv",
                "scope": self.scope.name,
                "path": self.path,
                "has_header": self.has_header,
            }
        )

    @staticmethod
    def from_json(data_source_dict):
        return CSVDataSourceEntity.create(
            name=data_source_dict.get("name"),
            scope=Scope[data_source_dict.get("scope")],
            path=data_source_dict.get("path"),
            has_header=data_source_dict.get("has_header"),
        )
