from datetime import datetime
from os.path import isfile
from typing import Any, Dict, List, Optional

import pandas as pd

from taipy.common.alias import DataSourceId, JobId
from taipy.data.data_source import DataSource
from taipy.data.scope import Scope
from taipy.exceptions import MissingRequiredProperty


class CSVDataSource(DataSource):
    """
    A Data Source stored as a CSV file.

    Note:
        The `properties` attribute must at least contain values for the "`path`" and
        "`has_header`" properties.
    """

    __STORAGE_TYPE = "csv"
    __REQUIRED_PROPERTIES = ["path", "has_header"]

    def __init__(
        self,
        config_name: str,
        scope: Scope,
        id: Optional[DataSourceId] = None,
        name: Optional[str] = None,
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
            name,
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
    def storage_type(cls) -> str:
        return cls.__STORAGE_TYPE

    def preview(self):
        df = pd.read_csv(self.path)
        print(df.head())

    def _read(self):
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
