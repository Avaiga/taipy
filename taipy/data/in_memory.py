import json
from typing import Any, Dict, Optional

from taipy.data.data_source import DataSource
from taipy.data.scope import Scope

in_memory_storage: Dict[str, Any] = {}


class InMemoryDataSource(DataSource):
    __TYPE = "in_memory"
    __DEFAULT_DATA_VALUE = "default_data"

    def __init__(
        self, config_name: str, scope: Scope, id: Optional[str] = None, parent_id: Optional[str] = None, properties=None
    ):
        if properties is None:
            properties = {}
        super().__init__(config_name, scope, id, parent_id or None, **properties)
        self._write_default_value_if_not_exist()

    def _write_default_value_if_not_exist(self):
        if self.properties.get(self.__DEFAULT_DATA_VALUE) is not None and self.id not in in_memory_storage:
            self.write(self.properties.get(self.__DEFAULT_DATA_VALUE))

    @classmethod
    def create(cls, config_name: str, scope: Scope, parent_id: Optional[str], data: Any = None):
        return InMemoryDataSource(config_name, scope, None, parent_id, {cls.__DEFAULT_DATA_VALUE: data})

    @classmethod
    def type(cls) -> str:
        return cls.__TYPE

    def preview(self):
        pass

    def read(self, query=None):
        return in_memory_storage.get(self.id)

    def write(self, data):
        in_memory_storage[self.id] = data
