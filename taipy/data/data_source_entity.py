import uuid
from abc import abstractmethod
from typing import Optional

from taipy.data.scope import Scope


class DataSourceEntity:
    """
    A class to represent a Data Source. A Data Source is an object that holds the name,
    scope and additional properties of the data entity.

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
        self, name, scope: Scope = Scope.PIPELINE, id: Optional[str] = None, **kwargs
    ):
        self.id = id or str(uuid.uuid4())
        self.name = name.strip().lower().replace(' ', '_')
        self.scope = scope
        self.properties = kwargs

    def __getattr__(self, attribute_name):
        property = self.properties[attribute_name]
        if property:
            return property
        else:
            return self.__getattr__(attribute_name)

    @classmethod
    @abstractmethod
    def type(cls) -> str:
        return NotImplemented

    @abstractmethod
    def preview(self):
        return NotImplemented

    @abstractmethod
    def get(self, query=None):
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
