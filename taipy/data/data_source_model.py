from dataclasses import dataclass
from typing import Any, Dict, Optional

from dataclasses_json import dataclass_json

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
    parent_id: str
        identifier of the parent (pipeline_id, scenario_id, bucket_id, None)
    data_source_properties: Dict[str, Any]
        extra properties of a DataSource
    """

    id: str
    config_name: str
    scope: Scope
    type: str
    parent_id: Optional[str]
    data_source_properties: Dict[str, Any]
