import logging
import uuid
from abc import abstractmethod
from typing import Optional

from taipy.data.scope import Scope


class DataSource:
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
        self.name = self.__protect_name(name)
        self.scope = scope
        self.properties = kwargs

    @staticmethod
    def __protect_name(name):
        return name.strip().lower().replace(' ', '_')

    def __getattr__(self, attribute_name):
        protected_attribute_name = self.__protect_name(attribute_name)
        if protected_attribute_name in self.properties:
            return self.properties[protected_attribute_name]
        logging.error(f"{attribute_name} is not an attribute of data source {self.id}")
        raise AttributeError

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
