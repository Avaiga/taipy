from datetime import datetime
from typing import Any, Dict, List, Optional

from taipy.common.alias import DataSourceId, JobId
from taipy.data.data_source import DataSource
from taipy.data.scope import Scope

in_memory_storage: Dict[str, Any] = {}


class InMemoryDataSource(DataSource):
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
        list of additional arguments. Note that at the creation of the data source, if the property default_data is
        present, the data source is automatically written with the corresponding default_data value.
    """

    __TYPE = "in_memory"
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
    def type(cls) -> str:
        return cls.__TYPE

    def preview(self):
        pass

    def _read(self, query=None):
        return in_memory_storage.get(self.id)

    def _write(self, data):
        in_memory_storage[self.id] = data
