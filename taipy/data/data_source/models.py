from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict


class Scope(Enum):
    """
    Class to represent the scope of usage of a Data Source
    """

    GLOBAL = 1
    TIME_BUCKET = 2
    SCENARIO = 3
    PIPELINE = 4


@dataclass
class DataSourceModel:
    """
    Class to hold a model of a DataSource. A model refers to the structure of a Data Source stored in a database.

    Attributes
    ----------
    id: int
        identifier of a DataSource
    name: int
        name of the DataSource
    scope: Scope
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
