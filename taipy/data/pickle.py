import os
import pickle
from datetime import datetime
from typing import Any, List, Optional

from taipy.common.alias import JobId
from taipy.data.data_source import DataSource
from taipy.data.scope import Scope


class PickleDataSource(DataSource):
    __TYPE = "pickle"
    __PICKLE_FILE_NAME = "file_path"
    __DEFAULT_DATA_VALUE = "default_data"

    def __init__(
        self,
        config_name: str,
        scope: Scope,
        id: Optional[str] = None,
        parent_id: Optional[str] = None,
        last_edition_date: Optional[datetime] = None,
        job_ids: List[JobId] = [],
        up_to_date: bool = False,
        properties=None,
    ):
        if properties is None:
            properties = {}
        super().__init__(config_name, scope, id, parent_id, last_edition_date, job_ids, up_to_date, **properties)
        self.__pickle_file_path = self.properties.get(self.__PICKLE_FILE_NAME) or f"{self.id}.p"
        if self.properties.get(self.__DEFAULT_DATA_VALUE) is not None and not os.path.exists(self.__pickle_file_path):
            self.write(self.properties.get(self.__DEFAULT_DATA_VALUE))

    @classmethod
    def create(
        cls,
        config_name: str,
        scope: Scope,
        parent_id: Optional[str],
        last_edition_date: Optional[datetime] = None,
        job_ids: List[JobId] = None,
        up_to_date: bool = False,
        data: Any = None,
        file_path: str = None,
    ):
        return PickleDataSource(
            config_name,
            scope,
            None,
            parent_id,
            last_edition_date,
            job_ids or [],
            up_to_date,
            {cls.__DEFAULT_DATA_VALUE: data, cls.__PICKLE_FILE_NAME: file_path},
        )

    @classmethod
    def type(cls) -> str:
        return cls.__TYPE

    def preview(self):
        pass

    def _read(self, query=None):
        return pickle.load(open(self.__pickle_file_path, "rb"))

    def _write(self, data):
        pickle.dump(data, open(self.__pickle_file_path, "wb"))
