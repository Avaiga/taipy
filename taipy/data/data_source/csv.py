import csv
from itertools import islice
from typing import Dict, Optional

from taipy.exceptions import MissingRequiredProperty

from .data_source import DataSource


class CSVDataSource(DataSource):
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

    def __init__(self, name: str, scope: int, id: Optional[str], properties: Dict):
        if missing := set(self.__REQUIRED_PROPERTIES) - set(properties.keys()):
            raise MissingRequiredProperty(
                f"The following properties {','.join(x for x in missing)} were not informed and are required"
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
        scope: int,
        path: str,
        has_header: bool = False,
        id: Optional[str] = None,
    ) -> DataSource:
        return CSVDataSource(name, scope, id, {"path": path, "has_header": has_header})

    def preview(self):
        print("------------CSV Content------------")
        path = self.properties.get("path")
        with open(path) as csv_file:
            reader = csv.DictReader(csv_file)
            for row in islice(reader, 5):
                print(f"     {row}")
        print("     ...")

    def get(self, query):
        pass

    @property
    def has_header(self) -> bool:
        return self.properties.get("has_header")

    @property
    def path(self) -> str:
        return self.properties.get("path")
