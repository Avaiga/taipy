import csv
import pandas as pd
import json
from itertools import islice
from typing import Dict, Optional

from taipy.data.data_source.data_source_entity import DataSourceEntity
from taipy.data.data_source.models import Scope
from taipy.exceptions import MissingRequiredProperty


class CSVDataSourceEntity(DataSourceEntity):
    """
    A class to represent a CSV Data Source.

    Attributes
    ----------
    name: str
        name that identifies the data source
    scope: int
        number that refers to the scope of usage of the data source
    properties: list
        list of additional arguments
    """

    __REQUIRED_PROPERTIES = ["path", "has_header"]

    def __init__(
        self, name: str, scope: Scope, id: Optional[str] = None, properties: Dict = {}
    ):
        if missing := set(self.__REQUIRED_PROPERTIES) - set(properties.keys()):
            raise MissingRequiredProperty(
                f"The following properties {', '.join(x for x in missing)} were not informed and are required"
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
        id: Optional[str] = None,
    ) -> DataSourceEntity:
        return CSVDataSourceEntity(
            name, scope, id, {"path": path, "has_header": has_header}
        )

    @property
    def type(self) -> str:
        return "csv"

    def preview(self):
        print("------------CSV Content------------")
        path = self.properties.get("path")
        with open(path) as csv_file:
            reader = csv.DictReader(csv_file)
            for row in islice(reader, 5):
                print(f"     {row}")
        print("     ...")

    def get(self, query):
        return pd.read_csv(self.properties["path"],index_col='DATE')

    def write(self, data):
        pass

    @property
    def has_header(self) -> Optional[bool]:
        return self.properties.get("has_header")

    @property
    def path(self) -> Optional[str]:
        return self.properties.get("path")

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
