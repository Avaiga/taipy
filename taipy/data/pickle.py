import os
import pickle
from typing import Any, Optional

from taipy.data.data_source import DataSource
from taipy.data.scope import Scope


class PickleDataSource(DataSource):
    __TYPE = "pickle"
    __PICKLE_FILE_NAME = "file_path"
    __DEFAULT_DATA_VALUE = "data"

    def __init__(
        self, config_name: str, scope: Scope, id: Optional[str] = None, parent_id: Optional[str] = None, properties=None
    ):
        if properties is None:
            properties = {}
        super().__init__(config_name, scope, id, parent_id or None, **properties)
        self.__pickle_file_path = self.properties.get(self.__PICKLE_FILE_NAME) or f"{self.id}.p"
        self._write_default_value_if_not_exist()

    def _write_default_value_if_not_exist(self):
        if self.properties.get(self.__DEFAULT_DATA_VALUE) is not None and not os.path.exists(self.__pickle_file_path):
            self.write(self.properties.get(self.__DEFAULT_DATA_VALUE))

    @classmethod
    def create(cls, config_name: str, scope: Scope, parent_id: Optional[str], data: Any = None, file_path: str = None):
        return PickleDataSource(
            config_name, scope, None, parent_id, {cls.__DEFAULT_DATA_VALUE: data, cls.__PICKLE_FILE_NAME: file_path}
        )

    @classmethod
    def type(cls) -> str:
        return cls.__TYPE

    def preview(self):
        pass

    def read(self, query=None):
        return pickle.load(open(self.__pickle_file_path, "rb"))

    def write(self, data):
        pickle.dump(data, open(self.__pickle_file_path, "wb"))
