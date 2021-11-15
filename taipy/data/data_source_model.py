from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from dataclasses_json import dataclass_json

from taipy.common.alias import JobId
from taipy.data.scope import Scope


@dataclass_json
@dataclass
class DataSourceModel:
    """
    Class to hold a model of a DataSource. A model refers to the structure of a
    Data Source stored in a database.

    Attributes
    ----------
    id: str
        identifier of a DataSource
    config_name: int
        name of the DataSourceConfig
    scope: taipy.data.source.scope.Scope
        scope of usage of a DataSource
    type: str
        name of the class that represents a DataSource
    name: str
        Displayable name of the DataSource
    parent_id: str
        identifier of the parent (pipeline_id, scenario_id, bucket_id, None)
    last_computation_date: str
        isoformat of the last computation datetime
    job_ids: List[str]
        list of jobs that computed the data source
    data_source_properties: Dict[str, Any]
        extra properties of a DataSource

    Key
    ---
    The tuple config_name and parent_id formed a unique key
    """

    id: str
    config_name: str
    scope: Scope
    type: str
    name: str
    parent_id: Optional[str]
    last_edition_date: Optional[str]
    job_ids: List[JobId]
    up_to_date: bool
    data_source_properties: Dict[str, Any]
