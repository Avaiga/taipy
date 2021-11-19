import logging
import uuid
from abc import abstractmethod
from datetime import datetime
from typing import List, Optional

from taipy.common import protect_name
from taipy.common.alias import DataSourceId, JobId
from taipy.data.scope import Scope
from taipy.exceptions.data_source import NoData


class DataSource:
    """
    A Data Source object.
    
    Data Sources hold the name, scope and additional properties of the data.

    Attributes:
        config_name (str):  Name that identifies the data source.

            We strongly recommend to use lowercase alphanumeric characters, dash characters ('-'),
            or underscore characters ('_').  
            Other characters are replaced according the following rules:

            - Space characters are replaced by underscore characters ('_').
            - Unicode characters are replaced by a corresponding alphanumeric character using the Unicode library.
            - Other characters are replaced by dash characters ('-').

        scope (Scope):  The usage scope of this data source.
        id (str): Unique identifier of this data source.
        str (str):  User-readable name of the data source.
        parent_id (str):  Identifier of the parent (pipeline_id, scenario_id, cycle_id) or `None`.
        last_edition_date (datetime):  Date and time of the last edition.
        job_ids (List[str]): Ordered list of jobs that have written this data source.
        up_to_date (bool): `True` if the data is considered as up to date. `False` otherwise.
        properties (list):  List of additional arguments.
    """

    __ID_PREFIX = "DATASOURCE"
    __ID_SEPARATOR = "_"

    def __init__(
        self,
        config_name,
        scope: Scope = Scope.PIPELINE,
        id: Optional[DataSourceId] = None,
        name: Optional[str] = None,
        parent_id: Optional[str] = None,
        last_edition_date: Optional[datetime] = None,
        job_ids: List[JobId] = None,
        up_to_date: bool = False,
        **kwargs,
    ):
        self.config_name = protect_name(config_name)
        self.id = id or DataSourceId(self.__ID_SEPARATOR.join([self.__ID_PREFIX, self.config_name, str(uuid.uuid4())]))
        self.name = name or self.id
        self.parent_id = parent_id
        self.scope = scope
        self.last_edition_date = last_edition_date
        self.job_ids = job_ids or []
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

    def __getattr__(self, attribute_name):
        protected_attribute_name = protect_name(attribute_name)
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
