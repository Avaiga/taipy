import dataclasses
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from taipy.common.alias import JobId
from taipy.data.scope import Scope


@dataclass
class DataSourceModel:
    """
    The model of a DataSource.

    A model refers to the structure of a Data Source stored in a database.

    Attributes:
        id (str): Identifier of a DataSource.
        config_name (int): Name of the `DataSourceConfig`.
        scope (taipy.data.source.scope.Scope): Scope of the usage of a DataSource.
        type (str):  Name of the class that represents a DataSource.
        name (str): User-readable name of the data source.
        parent_id (str): Identifier of the parent (pipeline_id, scenario_id, cycle_id) or `None`.
        last_edition_date (str): ISO format of the last edition date and time.
        job_ids (List[str]): List of jobs that computed the data source.
        edition_in_progress (bool): True if a task computing this data source has been submitted and not completed yet.
            False otherwise.
        data_source_properties (Dict[str, Any]): Additional properties of the data source.

    Note:
        The tuple `(config_name, parent_id)` forms a unique key.
    """

    id: str
    config_name: str
    scope: Scope
    storage_type: str
    name: str
    parent_id: Optional[str]
    last_edition_date: Optional[str]
    job_ids: List[JobId]
    validity_days: Optional[int]
    validity_hours: Optional[int]
    validity_minutes: Optional[int]
    edition_in_progress: bool
    data_source_properties: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {**dataclasses.asdict(self), "scope": repr(self.scope)}

    @staticmethod
    def from_dict(data: Dict[str, Any]):
        return DataSourceModel(
            id=data["id"],
            config_name=data["config_name"],
            scope=Scope.from_repr(data["scope"]),
            storage_type=data["storage_type"],
            name=data["name"],
            parent_id=data["parent_id"],
            last_edition_date=data["last_edition_date"],
            job_ids=data["job_ids"],
            validity_days=int(data["validity_days"]) if data["validity_days"] else None,
            validity_hours=int(data["validity_hours"]) if data["validity_hours"] else None,
            validity_minutes=int(data["validity_minutes"]) if data["validity_minutes"] else None,
            edition_in_progress=bool(data["edition_in_progress"]),
            data_source_properties=data["data_source_properties"],
        )
