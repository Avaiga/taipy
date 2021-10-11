from dataclasses import dataclass
from typing import Any, Dict

from taipy.data.scope import Scope


@dataclass
class DataSourceModel:
    """
    Class to hold a model of a DataSource. A model refers to the structure of a
    Data Source stored in a database.

    Attributes
    ----------
    id: int
        identifier of a DataSource
    name: int
        name of the DataSourceConfig
    scope: taipy.data.source.scope.Scope
        scope of usage of a DataSource
    type: str
        name of the class that represents a DataSource
    data_source_properties: Dict[str, Any]
        extra properties of a DataSource
    """

    id: str
    name: str
    scope: Scope
    type: str
    data_source_properties: Dict[str, Any]
