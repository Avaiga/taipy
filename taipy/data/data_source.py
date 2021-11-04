import logging
import uuid
from abc import abstractmethod
from datetime import date, datetime
from typing import List, Optional

from taipy.common.alias import JobId
from taipy.data.scope import Scope
from taipy.exceptions.data_source import NoData


class DataSource:
    """
    A class to represent a Data Source. A Data Source is an object that holds the name,
    scope and additional properties of the data.

    Attributes
    ----------
    id: str
        unique identifier of the data source
    config_name: str
        name that identifies the data source
    scope: int
        number that refers to the scope of usage of the data source
    parent_id: str
        identifier of the parent (pipeline_id, scenario_id, bucket_id, None)
    last_computation_date: str
        isoformat of the last computation datetime
    job_ids: List[str]
        list of jobs that computed the data source
    properties: list
        list of additional arguments
    """

    def __init__(
        self,
        config_name,
        scope: Scope = Scope.PIPELINE,
        id: Optional[str] = None,
        parent_id: Optional[str] = None,
        last_computation_date: Optional[datetime] = None,
        job_ids: List[JobId] = [],
        up_to_date: bool = False,
        **kwargs,
    ):
        self.id = id or str(uuid.uuid4())
        self.config_name = self.__protect_name(config_name)
        self.parent_id = parent_id
        self.scope = scope
        self.last_edition_date = last_computation_date
        self.job_ids = job_ids
        self.properties = kwargs
        self.up_to_date = up_to_date

    def __eq__(self, other):
        return self.id == other.id

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash(self.id)

    def __getstate__(self):
        return vars(self)

    def __setstate__(self, state):
        vars(self).update(state)

    @staticmethod
    def __protect_name(config_name: str):
        return config_name.strip().lower().replace(" ", "_")

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

    def read(self, query=None):
        if not self.last_edition_date:
            raise NoData
        return self._read(query)

    def write(self, data, job_id: Optional[JobId] = None):
        self._write(data)
        self.updated(job_id=job_id)

    def updated(self, at: Optional[datetime] = None, job_id: Optional[JobId] = None):
        self.last_edition_date = at or datetime.now()
        self.up_to_date = True
        if job_id:
            self.job_ids.append(job_id)

    def update_submitted(self):
        self.up_to_date = False

    @abstractmethod
    def _read(self, query=None):
        return NotImplemented

    @abstractmethod
    def _write(self, data):
        return NotImplemented
