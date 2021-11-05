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
    A class to represent a Data Source stored as a CSV file.

    Attributes
    ----------
    config_name: str
        Name that identifies the data source. We strongly recommend to use lowercase alphanumeric characters,
        dash character '-', or underscore character '_'.
        Note that other characters are replaced according the following rules :
        - Space character ' ' is replaced by '_'
        - Unicode characters are replaced by a corresponding alphanumeric character using unicode library
        - Other characters are replaced by dash character '-'
    scope: Scope
        Scope Enum that refers to the scope of usage of the data source
    id: str
        Unique identifier of the data source
    parent_id: str
        Identifier of the parent (pipeline_id, scenario_id, bucket_id, None)
    last_edition_date: datetime
        Date and time of the last edition
    job_ids: List[str]
        Ordered list of jobs that have written the data source
    up_to_date: bool
        True if the data is considered as up to date. False otherwise.
    properties: dict
        list of additional arguments. Note that the properties parameter should at least contain values for "path" and
        "has_header" properties.
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
        properties: Dict = None,
    ):
        if properties is None:
            properties = {}
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
