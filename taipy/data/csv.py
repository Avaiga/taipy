import csv
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
    __EXPOSED_TYPE_PROPERTY = "exposed_type"
    __REQUIRED_PATH_PROPERTY = "path"
    __REQUIRED_HAS_HEADER_PROPERTY = "has_header"
    __REQUIRED_PROPERTIES = [__REQUIRED_PATH_PROPERTY, __REQUIRED_HAS_HEADER_PROPERTY]

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
            config_name, scope, id, name, parent_id, last_edition_date, job_ids or [], up_to_date, **properties
        )
        if not self.last_edition_date and isfile(self.properties[self.__REQUIRED_PATH_PROPERTY]):
            self.updated()

    @classmethod
    def storage_type(cls) -> str:
        return cls.__STORAGE_TYPE

    def _read(self):
        if self.__EXPOSED_TYPE_PROPERTY in self.properties:
            return self._read_as(self.properties[self.__EXPOSED_TYPE_PROPERTY])
        return self._read_as_pandas_dataframe()

    def _read_as(self, custom_class):
        with open(self.properties[self.__REQUIRED_PATH_PROPERTY]) as csvFile:
            res = list()
            if self.properties[self.__REQUIRED_HAS_HEADER_PROPERTY]:
                reader = csv.DictReader(csvFile)
                for line in reader:
                    res.append(custom_class(**line))
            else:
                reader = csv.reader(
                    csvFile,
                )
                for line in reader:
                    res.append(custom_class(*line))
            return res

    def _read_as_pandas_dataframe(self, usecols: Optional[List[int]] = None, column_names: Optional[List[str]] = None):
        if self.properties[self.__REQUIRED_HAS_HEADER_PROPERTY]:
            if column_names:
                return pd.read_csv(self.properties[self.__REQUIRED_PATH_PROPERTY])[column_names]
            return pd.read_csv(self.properties[self.__REQUIRED_PATH_PROPERTY])
        else:
            if usecols:
                return pd.read_csv(self.properties[self.__REQUIRED_PATH_PROPERTY], header=None, usecols=usecols)
            return pd.read_csv(self.properties[self.__REQUIRED_PATH_PROPERTY], header=None)

    def _write(self, data: Any):
        pd.DataFrame(data).to_csv(self.properties[self.__REQUIRED_PATH_PROPERTY], index=False)

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
