import uuid
from abc import abstractmethod
from datetime import datetime, timedelta
from functools import reduce
from typing import List, Optional, Tuple, Union

import numpy as np
import pandas as pd

from taipy.core.common._entity import _Entity
from taipy.core.common._listattributes import _ListAttributes
from taipy.core.common._properties import _Properties
from taipy.core.common._reload import _reload, _self_reload, _self_setter
from taipy.core.common._taipy_logger import _TaipyLogger
from taipy.core.common._validate_id import _validate_id
from taipy.core.common.alias import DataNodeId, JobId
from taipy.core.config.data_node_config import DataNodeConfig
from taipy.core.data._filter import _FilterDataNode
from taipy.core.data.operator import JoinOperator, Operator
from taipy.core.data.scope import Scope
from taipy.core.exceptions.exceptions import NoData


class DataNode(_Entity):
    """
    Represents a reference to a dataset.

    A Data Node holds metadata related to the dataset it refers. In particular, a data node holds the name, the
    scope, the parent_id, the last edition date and some additional properties of the data. A data Node is also made to
    contain information and methods needed to access the dataset. This information depends on the type of storage, and
    it is hold by children classes (such as SQL Data Node, CSV Data Node, ...). It is strongly recommended to
    only instantiate children classes of Data Node through a Data Manager.

    Attributes:
        config_id (str): Identifier of the data node configuration. It must be a valid Python variable name.
        scope (`Scope^`): The `Scope^` of the data node.
        id (str): The unique identifier of the data node.
        name (str): A user-readable name of the data node.
        parent_id (str): The identifier of the parent (pipeline_id, scenario_id, cycle_id) or `None`.
        last_edition_date (datetime): The date and time of the last edition.
        job_ids (List[str]): The ordered list of jobs that have written this data node.
        validity_period (Optional[timedelta]): The validity period of a cacheable data node. Implemented as a
            timedelta. If _validity_period_ is set to None, the data_node is always up-to-date.
        edition_in_progress (bool): True if a task computing the data node has been submitted and not completed yet.
            False otherwise.
        kwargs: A dictionary of additional properties.
    """

    _ID_PREFIX = "DATANODE"
    __ID_SEPARATOR = "_"
    __logger = _TaipyLogger._get_logger()
    _REQUIRED_PROPERTIES: List[str] = []
    _MANAGER_NAME = "data"

    def __init__(
        self,
        config_id,
        scope: Scope = Scope(Scope.PIPELINE),
        id: Optional[DataNodeId] = None,
        name: Optional[str] = None,
        parent_id: Optional[str] = None,
        last_edition_date: Optional[datetime] = None,
        job_ids: List[JobId] = None,
        validity_period: Optional[timedelta] = None,
        edition_in_progress: bool = False,
        **kwargs,
    ):
        self.config_id = _validate_id(config_id)
        self.id = id or DataNodeId(self.__ID_SEPARATOR.join([self._ID_PREFIX, self.config_id, str(uuid.uuid4())]))
        self.parent_id = parent_id
        self._scope = scope
        self._last_edition_date = last_edition_date
        self._name = name or self.id
        self._edition_in_progress = edition_in_progress
        self._job_ids = _ListAttributes(self, job_ids or list())

        self._validity_period = validity_period

        self._properties = _Properties(self, **kwargs)

    @property  # type: ignore
    @_self_reload("data")
    def last_edition_date(self):
        return self._last_edition_date

    @last_edition_date.setter  # type: ignore
    @_self_setter(_MANAGER_NAME)
    def last_edition_date(self, val):
        self._last_edition_date = val

    @property  # type: ignore
    @_self_reload(_MANAGER_NAME)
    def scope(self):
        return self._scope

    @scope.setter  # type: ignore
    @_self_setter(_MANAGER_NAME)
    def scope(self, val):
        self._scope = val

    @property  # type: ignore
    @_self_reload("data")
    def validity_period(self) -> Optional[timedelta]:
        return self._validity_period if self._validity_period else None

    @validity_period.setter  # type: ignore
    @_self_setter(_MANAGER_NAME)
    def validity_period(self, val):
        self._validity_period = val

    @property  # type: ignore
    @_self_reload("data")
    def expiration_date(self) -> datetime:
        if not self._last_edition_date:
            raise NoData

        return self._last_edition_date + self.validity_period if self.validity_period else self._last_edition_date

    @property  # type: ignore
    @_self_reload("data")
    def name(self):
        return self._name

    @name.setter  # type: ignore
    @_self_setter(_MANAGER_NAME)
    def name(self, val):
        self._name = val

    @property  # type: ignore
    @_self_reload(_MANAGER_NAME)
    def edition_in_progress(self):
        return self._edition_in_progress

    @edition_in_progress.setter  # type: ignore
    @_self_setter(_MANAGER_NAME)
    def edition_in_progress(self, val):
        self._edition_in_progress = val

    @property  # type: ignore
    @_self_reload(_MANAGER_NAME)
    def job_ids(self):
        return self._job_ids

    @job_ids.setter  # type: ignore
    @_self_setter(_MANAGER_NAME)
    def job_ids(self, val):
        self._job_ids = _ListAttributes(self, val)

    @property  # type: ignore
    def properties(self):
        r = _reload("data", self)
        self._properties = r._properties
        return self._properties

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
        protected_attribute_name = _validate_id(attribute_name)
        if protected_attribute_name in self.properties:
            return self.properties[protected_attribute_name]
        raise AttributeError(f"{attribute_name} is not an attribute of data node {self.id}")

    @classmethod
    @abstractmethod
    def storage_type(cls) -> str:
        return NotImplemented

    def read_or_raise(self):
        """
        Read the data referenced by the data node.

        Returns:
            Any: The data referenced by the data node.
        Raises:
            `NoData^`: If the data has not been written yet.
        """
        if not self.last_edition_date:
            raise NoData
        return self._read()

    def read(self):
        """
        Read the data referenced by the data node.

        Returns:
            Any: The data referenced by the data node. None if the data has not been written yet.
        """
        try:
            return self.read_or_raise()
        except NoData:
            self.__logger.warning(f"Data node {self.id} is being read but has never been written.")
            return None

    def write(self, data, job_id: Optional[JobId] = None):
        """
        Write the _data_ given as parameter.

        Parameters:
            data (Any): The data to write.
            job_id (JobId): An optional identifier of the writer.
        """
        from taipy.core.data._data_manager import _DataManager

        self._write(data)
        self.unlock_edition(job_id=job_id)
        _DataManager._set(self)

    def lock_edition(self):
        """
        Locks the edition of the data node.

        Note:
            It can be unlocked with the method `(DataNode.)unlock_edition()^`
        """
        self.edition_in_progress = True

    def unlock_edition(self, at: datetime = None, job_id: JobId = None):
        """
        Unlocks the edition of the data node and update its _last_edition_date_.

        Parameters:
            at (datetime): The optional datetime of the last edition.
                If no _at_ datetime is provided, the current datetime is used.
            job_id (JobId): An optional identifier of the writer.
        Note:
            It can be locked with the method `(DataNode.)lock_edition()^`
        """
        self.last_edition_date = at or datetime.now()  # type: ignore
        self.edition_in_progress = False  # type: ignore
        if job_id:
            self._job_ids.append(job_id)

    def filter(self, operators: Union[List, Tuple], join_operator=JoinOperator.AND):
        """
        Reads the data referenced by the data node filtered by the provided list of 3-tuples (key, value, `Operator^`).

        If multiple filter operators are provided, filtered data will be joined based on the join operator (_AND_ or
        _OR_).

        Parameters:
            operators (Union[List[Tuple], Tuple]): TODO
            join_operator (`JoinOperator^`): The `JoinOperator^` used to join the multiple filter 3-tuples.
        """
        data = self._read()
        if len(operators) == 0:
            return data
        if not ((type(operators[0]) == list) or (type(operators[0]) == tuple)):
            if isinstance(data, pd.DataFrame):
                return DataNode.__filter_dataframe_per_key_value(data, operators[0], operators[1], operators[2])
            if isinstance(data, List):
                return DataNode.__filter_list_per_key_value(data, operators[0], operators[1], operators[2])
        else:
            if isinstance(data, pd.DataFrame):
                return DataNode.__filter_dataframe(data, operators, join_operator=join_operator)
            if isinstance(data, List):
                return DataNode.__filter_list(data, operators, join_operator=join_operator)
        return NotImplemented

    @staticmethod
    def __filter_dataframe(df_data: pd.DataFrame, operators: Union[List, Tuple], join_operator=JoinOperator.AND):
        filtered_df_data = []
        if join_operator == JoinOperator.AND:
            how = "inner"
        elif join_operator == JoinOperator.OR:
            how = "outer"
        else:
            return NotImplemented
        for key, value, operator in operators:
            filtered_df_data.append(DataNode.__filter_dataframe_per_key_value(df_data, key, value, operator))
        return DataNode.__dataframe_merge(filtered_df_data, how) if filtered_df_data else pd.DataFrame()

    @staticmethod
    def __filter_dataframe_per_key_value(df_data: pd.DataFrame, key: str, value, operator: Operator):
        df_by_col = df_data[key]
        if operator == Operator.EQUAL:
            df_by_col = df_by_col == value
        if operator == Operator.NOT_EQUAL:
            df_by_col = df_by_col != value
        if operator == Operator.LESS_THAN:
            df_by_col = df_by_col < value
        if operator == Operator.LESS_OR_EQUAL:
            df_by_col = df_by_col <= value
        if operator == Operator.GREATER_THAN:
            df_by_col = df_by_col > value
        if operator == Operator.GREATER_OR_EQUAL:
            df_by_col = df_by_col >= value
        return df_data[df_by_col]

    @staticmethod
    def __dataframe_merge(df_list: List, how="inner"):
        return reduce(lambda df1, df2: pd.merge(df1, df2, how=how), df_list)

    @staticmethod
    def __filter_list(list_data: List, operators: Union[List, Tuple], join_operator=JoinOperator.AND):
        filtered_list_data = []
        for key, value, operator in operators:
            filtered_list_data.append(DataNode.__filter_list_per_key_value(list_data, key, value, operator))
        if len(filtered_list_data) == 0:
            return filtered_list_data
        if join_operator == JoinOperator.AND:
            return DataNode.__list_intersect(filtered_list_data)
        elif join_operator == JoinOperator.OR:
            return list(set(np.concatenate(filtered_list_data)))
        else:
            return NotImplemented

    @staticmethod
    def __filter_list_per_key_value(list_data: List, key: str, value, operator: Operator):
        filtered_list = []
        for row in list_data:
            row_value = getattr(row, key)
            if operator == Operator.EQUAL and row_value == value:
                filtered_list.append(row)
            if operator == Operator.NOT_EQUAL and row_value != value:
                filtered_list.append(row)
            if operator == Operator.LESS_THAN and row_value < value:
                filtered_list.append(row)
            if operator == Operator.LESS_OR_EQUAL and row_value <= value:
                filtered_list.append(row)
            if operator == Operator.GREATER_THAN and row_value > value:
                filtered_list.append(row)
            if operator == Operator.GREATER_OR_EQUAL and row_value >= value:
                filtered_list.append(row)
        return filtered_list

    @staticmethod
    def __list_intersect(list_data):
        return list(set(list_data.pop()).intersection(*map(set, list_data)))

    @abstractmethod
    def _read(self):
        return NotImplemented

    @abstractmethod
    def _write(self, data):
        return NotImplemented

    def __getitem__(self, items):
        return _FilterDataNode(self.id, self._read())[items]

    @property  # type: ignore
    @_self_reload("data")
    def is_ready_for_reading(self):
        """
        Returns `False` if the data is locked for edition or if the data has never been written. `True` otherwise.
        """
        if self._edition_in_progress:
            return False
        if not self._last_edition_date:
            # Never been written so it is not up-to-date
            return False
        return True

    @property  # type: ignore
    @_self_reload("data")
    def _is_in_cache(self):
        if not self._properties.get(DataNodeConfig._IS_CACHEABLE_KEY):
            return False
        if not self._last_edition_date:
            # Never been written so it is not up-to-date
            return False
        if not self._validity_period:
            # No validity period and cacheable so it is up-to-date
            return True
        if datetime.now() > self.expiration_date:
            # expiration_date has been passed
            return False
        return True
