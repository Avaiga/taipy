# Copyright 2023 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import os
import uuid
from abc import abstractmethod
from datetime import datetime, timedelta
from functools import reduce
from typing import Any, Dict, List, Optional, Set, Tuple, Union

import modin.pandas as modin_pd
import numpy as np
import pandas as pd

from taipy.config.common._validate_id import _validate_id
from taipy.config.common.scope import Scope
from taipy.logger._taipy_logger import _TaipyLogger

from .._entity._entity import _Entity
from .._entity._labeled import _Labeled
from .._entity._properties import _Properties
from .._entity._reload import _reload, _self_reload, _self_setter
from .._version._version_manager_factory import _VersionManagerFactory
from ..common._warnings import _warn_deprecated
from ..exceptions.exceptions import NoData
from ..job.job_id import JobId
from ._filter import _FilterDataNode
from .data_node_id import DataNodeId, Edit
from .operator import JoinOperator, Operator


class DataNode(_Entity, _Labeled):
    """Reference to a dataset.

    A Data Node is an abstract class that holds metadata related to the dataset it refers to.
    In particular, a data node holds the name, the scope, the owner identifier, the last
    edit date, and some additional properties of the data.<br/>
    A Data Node also contains information and methods needed to access the dataset. This
    information depends on the type of storage, and it is held by subclasses (such as
    SQL Data Node, CSV Data Node, ...).

    !!! note
        It is recommended not to instantiate subclasses of `DataNode` directly.

    Attributes:
        config_id (str): Identifier of the data node configuration. It must be a valid Python
            identifier.
        scope (Scope^): The scope of this data node.
        id (str): The unique identifier of this data node.
        name (str): A user-readable name of this data node.
        owner_id (str): The identifier of the owner (pipeline_id, scenario_id, cycle_id) or
            None.
        parent_ids (Optional[Set[str]]): The set of identifiers of the parent tasks.
        last_edit_date (datetime): The date and time of the last modification.
        edits (List[Edit^]): The list of Edits (an alias for dict) containing medata about each
            edition of that node.
        version (str): The string indicates the application version of the data node to
            instantiate. If not provided, the current version is used.
        validity_period (Optional[timedelta]): The validity period of a data node.
            Implemented as a timedelta. If *validity_period* is set to None, the data node is
            always up-to-date.
        edit_in_progress (bool): True if the data node is locked for modification. False
            otherwise.
        kwargs: A dictionary of additional properties.
    """

    _ID_PREFIX = "DATANODE"
    __ID_SEPARATOR = "_"
    __logger = _TaipyLogger._get_logger()
    _REQUIRED_PROPERTIES: List[str] = []
    _MANAGER_NAME = "data"
    __PATH_KEY = "path"

    def __init__(
        self,
        config_id,
        scope: Scope = Scope(Scope.SCENARIO),
        id: Optional[DataNodeId] = None,
        name: Optional[str] = None,
        owner_id: Optional[str] = None,
        parent_ids: Optional[Set[str]] = None,
        last_edit_date: Optional[datetime] = None,
        edits: Optional[List[Edit]] = None,
        version: Optional[str] = None,
        validity_period: Optional[timedelta] = None,
        edit_in_progress: bool = False,
        **kwargs,
    ):
        self.config_id = _validate_id(config_id)
        self.id = id or DataNodeId(self.__ID_SEPARATOR.join([self._ID_PREFIX, self.config_id, str(uuid.uuid4())]))
        self.owner_id = owner_id
        self._parent_ids = parent_ids or set()
        self._scope = scope
        self._last_edit_date = last_edit_date
        self._name = name
        self._edit_in_progress = edit_in_progress
        self._version = version or _VersionManagerFactory._build_manager()._get_latest_version()
        self._validity_period = validity_period

        # Track edits
        self._edits = edits or list()

        self._properties = _Properties(self, **kwargs)

    @property
    def parent_id(self):
        """Deprecated. Use `owner_id` instead."""
        _warn_deprecated("parent_id", suggest="owner_id")
        return self.owner_id

    @parent_id.setter
    def parent_id(self, val):
        """Deprecated. Use `owner_id` instead."""
        _warn_deprecated("parent_id", suggest="owner_id")
        self.owner_id = val

    def get_parents(self):
        """Get all parents of this data node."""
        from ... import core as tp

        return tp.get_parents(self)

    @property  # type: ignore
    @_self_reload(_MANAGER_NAME)
    def parent_ids(self):
        """List of parent ids of this data node."""
        return self._parent_ids

    @property  # type: ignore
    @_self_reload(_MANAGER_NAME)
    def edits(self):
        """Get all `Edit^`s of this data node."""
        return self._edits

    def get_last_edit(self) -> Optional[Edit]:
        """Get last `Edit^` of this data node.

        Returns:
            None if there has been no `Edit^` on this data node.
        """
        if self._edits:
            return self._edits[-1]
        return None

    @property  # type: ignore
    @_self_reload(_MANAGER_NAME)
    def last_edit_date(self):
        last_modified_datetime = self.__get_last_modified_datetime()
        if last_modified_datetime and last_modified_datetime > self._last_edit_date:
            return last_modified_datetime
        else:
            return self._last_edit_date

    @last_edit_date.setter  # type: ignore
    @_self_setter(_MANAGER_NAME)
    def last_edit_date(self, val):
        self._last_edit_date = val

    @property
    def last_edition_date(self):
        """Deprecated. Use `last_edit_date` instead."""
        _warn_deprecated("last_edition_date", suggest="last_edit_date")
        return self.last_edit_date

    @last_edition_date.setter
    def last_edition_date(self, val):
        _warn_deprecated("last_edition_date", suggest="last_edit_date")
        self.last_edit_date = val

    @property  # type: ignore
    @_self_reload(_MANAGER_NAME)
    def scope(self):
        return self._scope

    @scope.setter  # type: ignore
    @_self_setter(_MANAGER_NAME)
    def scope(self, val):
        self._scope = val

    @property  # type: ignore
    @_self_reload(_MANAGER_NAME)
    def validity_period(self) -> Optional[timedelta]:
        return self._validity_period if self._validity_period else None

    @validity_period.setter  # type: ignore
    @_self_setter(_MANAGER_NAME)
    def validity_period(self, val):
        self._validity_period = val

    @property  # type: ignore
    @_self_reload(_MANAGER_NAME)
    def expiration_date(self) -> datetime:
        """Datetime instant of the expiration date of this data node."""
        last_edit_date = self.last_edit_date
        validity_period = self._validity_period

        if not last_edit_date:
            raise NoData(f"Data node {self.id} from config {self.config_id} has not been written yet.")

        return last_edit_date + validity_period if validity_period else last_edit_date

    @property  # type: ignore
    @_self_reload(_MANAGER_NAME)
    def name(self):
        return self._name

    @name.setter  # type: ignore
    @_self_setter(_MANAGER_NAME)
    def name(self, val):
        self._name = val

    @property
    def version(self):
        return self._version

    @property
    def cacheable(self):
        """Deprecated. Use `skippable` attribute of a `Task^` instead."""
        _warn_deprecated("cacheable", suggest="the skippable feature")
        return self.properties.get("cacheable", False)

    @cacheable.setter
    def cacheable(self, val):
        _warn_deprecated("cacheable", suggest="the skippable feature")

    @property  # type: ignore
    @_self_reload(_MANAGER_NAME)
    def edit_in_progress(self):
        return self._edit_in_progress

    @edit_in_progress.setter  # type: ignore
    @_self_setter(_MANAGER_NAME)
    def edit_in_progress(self, val):
        self._edit_in_progress = val

    @property
    def edition_in_progress(self):
        """Deprecated. Use `edit_in_progress` instead."""
        _warn_deprecated("edition_in_progress", suggest="edit_in_progress")
        return self.edit_in_progress

    @edition_in_progress.setter
    def edition_in_progress(self, val):
        """Deprecated. Use `edit_in_progress` instead."""
        _warn_deprecated("edition_in_progress", suggest="edit_in_progress")
        self.edit_in_progress = val

    @property  # type: ignore
    @_self_reload(_MANAGER_NAME)
    def job_ids(self):
        """List of the jobs having edited this data node."""
        return [edit.get("job_id") for edit in self.edits if edit.get("job_id")]

    @property
    def properties(self):
        """Dictionary of custom properties."""
        r = _reload(self._MANAGER_NAME, self)
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
        if protected_attribute_name in self._properties:
            return self._properties[protected_attribute_name]
        raise AttributeError(f"{attribute_name} is not an attribute of data node {self.id}")

    def __get_last_modified_datetime(self) -> Optional[datetime]:
        path = self._properties.get(self.__PATH_KEY, None)
        if path and os.path.isfile(path):
            return datetime.fromtimestamp(os.path.getmtime(path))

        last_modified_datetime = None
        if path and os.path.isdir(path):
            for filename in os.listdir(path):
                filepath = os.path.join(path, filename)
                if os.path.isfile(filepath):
                    file_mtime = datetime.fromtimestamp(os.path.getmtime(filepath))

                    if last_modified_datetime is None or file_mtime > last_modified_datetime:
                        last_modified_datetime = file_mtime

        return last_modified_datetime

    @classmethod
    @abstractmethod
    def storage_type(cls) -> str:
        return NotImplementedError  # type: ignore

    def read_or_raise(self) -> Any:
        """Read the data referenced by this data node.

        Returns:
            The data referenced by this data node.

        Raises:
            NoData^: If the data has not been written yet.
        """
        if not self.last_edit_date:
            raise NoData(f"Data node {self.id} from config {self.config_id} has not been written yet.")
        return self._read()

    def read(self) -> Any:
        """Read the data referenced by this data node.

        Returns:
            The data referenced by this data node. None if the data has not been written yet.
        """
        try:
            return self.read_or_raise()
        except NoData:
            self.__logger.warning(
                f"Data node {self.id} from config {self.config_id} is being read but has never been " f"written."
            )
            return None

    def write(self, data, job_id: Optional[JobId] = None, **kwargs: Dict[str, Any]):
        """Write some data to this data node.

        Parameters:
            data (Any): The data to write to this data node.
            job_id (JobId^): An optional identifier of the writer.
            **kwargs (dict[str, any]): Extra information to attach to the edit document
                corresponding to this write.
        """
        from ._data_manager_factory import _DataManagerFactory

        self._write(data)
        self._track_edit(job_id=job_id, **kwargs)
        self.unlock_edit()
        _DataManagerFactory._build_manager()._set(self)

    def _track_edit(self, **options):
        """Add Edit tracking information to this data node."""
        edit = {}
        for k, v in options.items():
            if v is not None:
                edit[k] = v
        if "timestamp" not in edit:
            edit["timestamp"] = datetime.now()
        self.last_edit_date = edit.get("timestamp")
        self._edits.append(edit)

    def lock_edit(self):
        """Lock the data node modification.

        Note:
            The data node can be unlocked with the method `(DataNode.)unlock_edit()^`.
        """
        self.edit_in_progress = True

    def lock_edition(self):
        """Deprecated. Use `lock_edit` instead."""
        _warn_deprecated("lock_edition", suggest="lock_edit")
        self.lock_edit()

    def unlock_edit(self, at: Optional[datetime] = None, job_id: Optional[JobId] = None):
        """Unlocks the data node modification.

        Parameters:
            at (Optional[datetime]): Deprecated.
            job_id (Optional[JobId^]): Deprecated.

        Note:
            The data node can be locked with the method `(DataNode.)lock_edit()^`.
        """
        self.edit_in_progress = False  # type: ignore

    def unlock_edition(self, at: Optional[datetime] = None, job_id: Optional[JobId] = None):
        """Deprecated. Use `(DataNode.)unlock_edit()^` instead."""
        _warn_deprecated("unlock_edition", suggest="unlock_edit")
        self.unlock_edit()

    def filter(self, operators: Union[List, Tuple], join_operator=JoinOperator.AND):
        """Read and filter the data referenced by this data node.

        The data is filtered by the provided list of 3-tuples (key, value, `Operator^`).

        If multiple filter operators are provided, filtered data will be joined based on the
        join operator (_AND_ or _OR_).

        Parameters:
            operators (Union[List[Tuple], Tuple]): TODO
            join_operator (JoinOperator^): The operator used to join the multiple filter
                3-tuples.
        """
        data = self._read()
        if len(operators) == 0:
            return data
        if not ((type(operators[0]) == list) or (type(operators[0]) == tuple)):
            if isinstance(data, (pd.DataFrame, modin_pd.DataFrame)):
                return DataNode.__filter_dataframe_per_key_value(data, operators[0], operators[1], operators[2])
            if isinstance(data, List):
                return DataNode.__filter_list_per_key_value(data, operators[0], operators[1], operators[2])
        else:
            if isinstance(data, (pd.DataFrame, modin_pd.DataFrame)):
                return DataNode.__filter_dataframe(data, operators, join_operator=join_operator)
            if isinstance(data, List):
                return DataNode.__filter_list(data, operators, join_operator=join_operator)
        return NotImplementedError

    @staticmethod
    def __filter_dataframe(
        df_data: Union[pd.DataFrame, modin_pd.DataFrame], operators: Union[List, Tuple], join_operator=JoinOperator.AND
    ):
        filtered_df_data = []
        if join_operator == JoinOperator.AND:
            how = "inner"
        elif join_operator == JoinOperator.OR:
            how = "outer"
        else:
            return NotImplementedError
        for key, value, operator in operators:
            filtered_df_data.append(DataNode.__filter_dataframe_per_key_value(df_data, key, value, operator))
        return DataNode.__dataframe_merge(filtered_df_data, how) if filtered_df_data else pd.DataFrame()

    @staticmethod
    def __filter_dataframe_per_key_value(
        df_data: Union[pd.DataFrame, modin_pd.DataFrame], key: str, value, operator: Operator
    ):
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
            return NotImplementedError

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
        raise NotImplementedError

    @abstractmethod
    def _write(self, data):
        raise NotImplementedError

    def __getitem__(self, items):
        return _FilterDataNode(self.id, self._read())[items]

    @property  # type: ignore
    @_self_reload(_MANAGER_NAME)
    def is_ready_for_reading(self) -> bool:
        """Indicate if this data node is ready for reading.

        Returns:
            False if the data is locked for modification or if the data has never been written.
                True otherwise.
        """
        if self._edit_in_progress:
            return False
        if not self._last_edit_date:
            # Never been written so it is not up-to-date
            return False
        return True

    @property  # type: ignore
    @_self_reload(_MANAGER_NAME)
    def is_up_to_date(self) -> bool:
        """Indicate if this data node is up-to-date.

        Returns:
            False if the data ever been written or the expiration date has passed.<br/>
            True otherwise.
        """
        if not self._last_edit_date:
            # Never been written so it is not up-to-date
            return False
        if not self._validity_period:
            # No validity period and has already been written, so it is up-to-date
            return True
        if datetime.now() > self.expiration_date:
            # expiration_date has been passed
            return False
        return True

    @staticmethod
    def _class_map():
        def all_subclasses(cls):
            subclasses = set(cls.__subclasses__())
            for s in cls.__subclasses__():
                subclasses.update(all_subclasses(s))
            return subclasses

        return {c.storage_type(): c for c in all_subclasses(DataNode) if c.storage_type() is not None}

    def get_label(self) -> str:
        """Returns the data node simple label prefixed by its owner label.

        Returns:
            The label of the data node as a string.
        """
        return self._get_label()

    def get_simple_label(self) -> str:
        """Returns the data node simple label.

        Returns:
            The simple label of the data node as a string.
        """
        return self._get_simple_label()
