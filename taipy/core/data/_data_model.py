import dataclasses
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from taipy.core.common.alias import JobId
from taipy.core.data.scope import Scope


@dataclass
class _DataNodeModel:

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
        return _DataNodeModel(
            id=data["id"],
            config_id=data["config_id"],
            scope=Scope._from_repr(data["scope"]),
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
