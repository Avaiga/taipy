import uuid
from abc import abstractmethod
from typing import Optional

from taipy.data.scope import Scope


class DataSourceEntity:
    """
    A class to represent a Data Source. A Data Source is an object that holds the name, scope and additional
    properties of the data entity.

    Attributes
    ----------
    id: str
        unique identifier of the data entity
    name: str
        name that identifies the data entity
    scope: int
        number that refers to the scope of usage of the data entity
    properties: list
        list of additional arguments
    """

    def __init__(
        self, name, scope: Scope = Scope.PIPELINE, id: Optional[str] = str(uuid.uuid4()), **kwargs
    ):
        self.id = id
        self.name = name
        self.scope = scope
        self.properties = kwargs

    @abstractmethod
    def type(self) -> str:
        return NotImplemented

    @abstractmethod
    def preview(self):
        return NotImplemented

    @abstractmethod
    def get(self, query):
        return NotImplemented

    @abstractmethod
    def write(self, data):
        """
        Temporary function interface, will be remove
        """
        return NotImplemented

    def to_json(self):
        pass

    def from_json(self):
        pass
