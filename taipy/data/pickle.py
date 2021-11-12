import os
import pickle
from datetime import datetime
from typing import Any, List, Optional

from taipy.common.alias import JobId
from taipy.data.data_source import DataSource
from taipy.data.scope import Scope


class PickleDataSource(DataSource):
    """
    A class to represent a Data Source stored as a pickle file.

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
        list of additional arguments.
        Note that at the creation of the data source, if the property default_data is
        present, the data source is automatically written with the corresponding default_data value.
        If the property file_path is present, data will be stored using the corresponding value as the name of the file.
    """

    __TYPE = "pickle"
    __PICKLE_FILE_NAME = "file_path"
    __DEFAULT_DATA_VALUE = "default_data"

    def __init__(
        self,
        config_name: str,
        scope: Scope,
        id: Optional[str] = None,
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
