import dataclasses
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from taipy.core.common.alias import JobId
from taipy.core.data.scope import Scope


@dataclass
class DataNodeModel:
    """
    The model of a DataNode.

    A model refers to the structure of a Data Node stored in a database.

    Attributes:
        id (str): Identifier of a DataNode.
        config_id (int): Identifier of the `DataNodeConfig`.
        scope (taipy.core.data.node.scope.Scope): Scope of the usage of a DataNode.
        type (str):  Name of the class that represents a DataNode.
        name (str): User-readable name of the data node.
        parent_id (str): Identifier of the parent (pipeline_id, scenario_id, cycle_id) or `None`.
        last_edition_date (str): ISO format of the last edition date and time.
        job_ids (List[str]): List of jobs that computed the data node.
        validity_period (Optional[timedelta]): Number of weeks, days, hours, minutes, and seconds as a
            timedelta object to represent the data node validity duration. If validity_period is set to None,
            the data_node is always up to date.
        validity_days (Optional[float]): Number of days to be added to the data node validity duration. If
            validity_days and validity_seconds are all set to None, The data_node is always up to
            date.
        validity_seconds (Optional[float]): Number of seconds to be added to the data node validity duration. If
            validity_days and validity_seconds are all set to None, The data_node is always up to
            date.
        edition_in_progress (bool): True if a task computing this data node has been submitted and not completed yet.
            False otherwise.
        data_node_properties (Dict[str, Any]): Additional properties of the data node.

    Note:
        The tuple `(config_id, parent_id)` forms a unique key.
    """

    id: str
    config_id: str
    scope: Scope
    storage_type: str
    name: str
    parent_id: Optional[str]
    last_edition_date: Optional[str]
    job_ids: List[JobId]
    validity_days: Optional[float]
    validity_seconds: Optional[float]
    edition_in_progress: bool
    data_node_properties: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {**dataclasses.asdict(self), "scope": repr(self.scope)}

    @staticmethod
    def from_dict(data: Dict[str, Any]):
        return DataNodeModel(
            id=data["id"],
            config_id=data["config_id"],
            scope=Scope.from_repr(data["scope"]),
            storage_type=data["storage_type"],
            name=data["name"],
            parent_id=data["parent_id"],
            last_edition_date=data["last_edition_date"],
            job_ids=data["job_ids"],
            validity_days=data["validity_days"],
            validity_seconds=data["validity_seconds"],
            edition_in_progress=bool(data["edition_in_progress"]),
            data_node_properties=data["data_node_properties"],
        )
