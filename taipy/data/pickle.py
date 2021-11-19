import os
import pickle
from datetime import datetime
from typing import Any, List, Optional

from taipy.common.alias import DataSourceId, JobId
from taipy.data.data_source import DataSource
from taipy.data.scope import Scope


class PickleDataSource(DataSource):
    """
    A Data Source stored as a pickle file.

    Note:
        When the data source is created, if the property `default_data` is set, then the
        the data source is automatically written with the value of this `default_data` property.

        If the property `file_path` is present, data will be stored using the corresponding value
        as the path name of the pickle file.
    """

    __TYPE = "pickle"
    __PICKLE_FILE_NAME = "file_path"
    __DEFAULT_DATA_VALUE = "default_data"

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
        properties=None,
    ):
        if up_to_date is None:
            up_to_date = []
        if properties is None:
            properties = {}
        super().__init__(config_name, scope, id, name, parent_id, last_edition_date, job_ids, up_to_date, **properties)
        self.__pickle_file_path = self.properties.get(self.__PICKLE_FILE_NAME) or f"{self.id}.p"
        if self.properties.get(self.__DEFAULT_DATA_VALUE) is not None and not os.path.exists(self.__pickle_file_path):
            self.write(self.properties.get(self.__DEFAULT_DATA_VALUE))

    @classmethod
    def type(cls) -> str:
        return cls.__TYPE

    def preview(self):
        pass

    def _read(self, query=None):
        return pickle.load(open(self.__pickle_file_path, "rb"))

    def _write(self, data):
        pickle.dump(data, open(self.__pickle_file_path, "wb"))
