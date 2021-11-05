from datetime import datetime
from os.path import isfile
from typing import Any, Dict, List, Optional

import pandas as pd

from taipy.common.alias import JobId
from taipy.data.data_source import DataSource
from taipy.data.scope import Scope
from taipy.exceptions import MissingRequiredProperty


class CSVDataSource(DataSource):
    """
    A class to represent a CSV Data Source.

    Attributes
    ----------
    config_name: str
        name that identifies the data source config
    scope: int
        number that refers to the scope of usage of the data source
    properties: list
        list of additional arguments
    """

    __REQUIRED_PROPERTIES = ["path", "has_header"]
    __TYPE = "csv"

    def __init__(
        self,
        config_name: str,
        scope: Scope,
        id: Optional[str] = None,
        parent_id: Optional[str] = None,
        last_edition_date: Optional[datetime] = None,
        job_ids: List[JobId] = None,
        up_to_date: bool = False,
        properties: Dict = {},
    ):
        if missing := set(self.__REQUIRED_PROPERTIES) - set(properties.keys()):
            raise MissingRequiredProperty(
                f"The following properties " f"{', '.join(x for x in missing)} were not informed and are required"
            )
        super().__init__(
            config_name,
            scope,
            id,
            parent_id,
            last_edition_date,
            job_ids or [],
            up_to_date,
            path=properties.get("path"),
            has_header=properties.get("has_header"),
        )
        if not self.last_edition_date and isfile(self.properties["path"]):
            self.updated()

    @classmethod
    def create(
        cls,
        config_name: str,
        scope: Scope,
        parent_id: Optional[str],
        path: str,
        has_header: bool = False,
        last_edition_date: Optional[datetime] = None,
        up_to_date: bool = False,
        job_ids: List[JobId] = None,
    ) -> DataSource:
        return CSVDataSource(
            config_name,
            scope,
            None,
            parent_id,
            last_edition_date,
            job_ids or [],
            up_to_date,
            {"path": path, "has_header": has_header},
        )

    @classmethod
    def type(cls) -> str:
        return cls.__TYPE

    def preview(self):
        df = pd.read_csv(self.path)
        print(df.head())

    def _read(self, query=None):
        return pd.read_csv(self.properties["path"])

    def _write(self, data: Any):
        pd.DataFrame(data).to_csv(self.path, index=False)

    def write_with_column_names(self, data: Any, columns: List[str] = None, job_id: Optional[JobId] = None):
        if not columns:
            df = pd.DataFrame(data)
        else:
            df = pd.DataFrame(data, columns=columns)
        df.to_csv(self.path, index=False)
        self.last_edition_date = datetime.now()
        self.up_to_date = True
        if job_id:
            self.job_ids.append(job_id)
