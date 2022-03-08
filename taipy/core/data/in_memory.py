from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from taipy.core.common.alias import DataNodeId, JobId
from taipy.core.data.data_node import DataNode
from taipy.core.data.scope import Scope

in_memory_storage: Dict[str, Any] = {}


class InMemoryDataNode(DataNode):
    """
    A Data Node stored in memory.

    This Data Node implementation is not compatible with a parallel execution of taipy tasks, but only with a
    Synchronous task executor. The purpose of InMemoryDataNode is to be used for development or debug.

    Attributes:
        config_id (str):  Identifier of the data node configuration. Must be a valid Python variable name.
        scope (Scope):  The usage scope of this data node.
        id (str): Unique identifier of this data node.
        name (str): User-readable name of the data node.
        parent_id (str): Identifier of the parent (pipeline_id, scenario_id, cycle_id) or `None`.
        last_edition_date (datetime):  Date and time of the last edition.
        job_ids (List[str]): Ordered list of jobs that have written this data node.
        validity_period (Optional[timedelta]): Number of weeks, days, hours, minutes, and seconds as a
            timedelta object to represent the data node validity duration. If validity_period is set to None,
            the data_node is always up to date.
        properties (dict): Dict of additional arguments. Note that at the creation of the In Memory data node, if the
            property default_data is present, the data node is automatically written with the corresponding
            default_data value.
    """

    __STORAGE_TYPE = "in_memory"
    __DEFAULT_DATA_VALUE = "default_data"
    REQUIRED_PROPERTIES: List[str] = []

    def __init__(
        self,
        config_id: str,
        scope: Scope,
        id: Optional[DataNodeId] = None,
        name: Optional[str] = None,
        parent_id: Optional[str] = None,
        last_edition_date: Optional[datetime] = None,
        job_ids: List[JobId] = None,
        validity_period: Optional[timedelta] = None,
        edition_in_progress: bool = False,
        properties=None,
    ):
        if job_ids is None:
            job_ids = []
        if properties is None:
            properties = {}
        default_value = properties.pop(self.__DEFAULT_DATA_VALUE, None)
        super().__init__(
            config_id,
            scope,
            id,
            name,
            parent_id,
            last_edition_date,
            job_ids,
            validity_period,
            edition_in_progress,
            **properties
        )
        if default_value is not None and self.id not in in_memory_storage:
            self.write(default_value)

    @classmethod
    def storage_type(cls) -> str:
        return cls.__STORAGE_TYPE

    def _read(self):
        return in_memory_storage.get(self.id)

    def _write(self, data):
        in_memory_storage[self.id] = data
