from datetime import datetime
from typing import Any, Dict, List, Optional

from taipy.common.alias import DataSourceId, JobId
from taipy.data.data_source import DataSource
from taipy.data.scope import Scope

in_memory_storage: Dict[str, Any] = {}


class InMemoryDataSource(DataSource):
    """
    A Data Source stored in memory.

    Note:
        When the data source is created, if the property `default_data` is set, then the
        the data source is automatically written with the value of this `default_data` property.
    """

    __STORAGE_TYPE = "in_memory"
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
        if job_ids is None:
            job_ids = []
        if properties is None:
            properties = {}
        super().__init__(config_name, scope, id, name, parent_id, last_edition_date, job_ids, up_to_date, **properties)
        if self.properties.get(self.__DEFAULT_DATA_VALUE) is not None and self.id not in in_memory_storage:
            self.write(self.properties.get(self.__DEFAULT_DATA_VALUE))

    @classmethod
    def storage_type(cls) -> str:
        return cls.__STORAGE_TYPE

    def _read(self):
        return in_memory_storage.get(self.id)

    def _write(self, data):
        in_memory_storage[self.id] = data
