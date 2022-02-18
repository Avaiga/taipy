from datetime import datetime
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
        config_name (str):  Name that identifies the data node.
            We strongly recommend to use lowercase alphanumeric characters, dash character '-', or underscore character
            '_'. Note that other characters are replaced according the following rules :
            - Space characters are replaced by underscore characters ('_').
            - Unicode characters are replaced by a corresponding alphanumeric character using the Unicode library.
            - Other characters are replaced by dash characters ('-').
        scope (Scope):  The usage scope of this data node.
        id (str): Unique identifier of this data node.
        name (str): User-readable name of the data node.
        parent_id (str): Identifier of the parent (pipeline_id, scenario_id, cycle_id) or `None`.
        last_edition_date (datetime):  Date and time of the last edition.
        job_ids (List[str]): Ordered list of jobs that have written this data node.
        up_to_date (bool): `True` if the data is considered as up to date. `False` otherwise.
        properties (dict): Dict of additional arguments. Note that at the creation of the In Memory data node, if the
            property default_data is present, the data node is automatically written with the corresponding
            default_data value.
    """

    __STORAGE_TYPE = "in_memory"
    __DEFAULT_DATA_VALUE = "default_data"

    def __init__(
        self,
        config_name: str,
        scope: Scope,
        id: Optional[DataNodeId] = None,
        name: Optional[str] = None,
        parent_id: Optional[str] = None,
        last_edition_date: Optional[datetime] = None,
        job_ids: List[JobId] = None,
        validity_days: Optional[int] = None,
        validity_hours: Optional[int] = None,
        validity_minutes: Optional[int] = None,
        edition_in_progress: bool = False,
        properties=None,
    ):
        if job_ids is None:
            job_ids = []
        if properties is None:
            properties = {}
        default_value = properties.pop(self.__DEFAULT_DATA_VALUE, None)
        super().__init__(
            config_name,
            scope,
            id,
            name,
            parent_id,
            last_edition_date,
            job_ids,
            validity_days,
            validity_hours,
            validity_minutes,
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
