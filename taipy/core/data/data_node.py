# Copyright 2021-2024 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import functools
import os
import uuid
from abc import abstractmethod
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Tuple, Union

import networkx as nx

from taipy.common.config.common._validate_id import _validate_id
from taipy.common.config.common.scope import Scope
from taipy.common.logger._taipy_logger import _TaipyLogger

from .._entity._entity import _Entity
from .._entity._labeled import _Labeled
from .._entity._properties import _Properties
from .._entity._ready_to_run_property import _ReadyToRunProperty
from .._entity._reload import _Reloader, _self_reload, _self_setter
from .._version._version_manager_factory import _VersionManagerFactory
from ..exceptions.exceptions import DataNodeIsBeingEdited, NoData
from ..job.job_id import JobId
from ..notification.event import Event, EventEntityType, EventOperation, _make_event
from ..reason import DataNodeEditInProgress, DataNodeIsNotWritten
from ._filter import _FilterDataNode
from .data_node_id import DataNodeId, Edit
from .operator import JoinOperator


def _update_ready_for_reading(fct):
    # This decorator must be wrapped before self_setter decorator as self_setter will run the function twice.
    @functools.wraps(fct)
    def _recompute_is_ready_for_reading(dn: "DataNode", *args, **kwargs):
        fct(dn, *args, **kwargs)
        if dn._edit_in_progress:
            _ReadyToRunProperty._add(dn, DataNodeEditInProgress(dn.id))
        else:
            _ReadyToRunProperty._remove(dn, DataNodeEditInProgress(dn.id))
        if not dn._last_edit_date:
            _ReadyToRunProperty._add(dn, DataNodeIsNotWritten(dn.id))
        else:
            _ReadyToRunProperty._remove(dn, DataNodeIsNotWritten(dn.id))

    return _recompute_is_ready_for_reading


class DataNode(_Entity, _Labeled):
    """Reference to a dataset.

    A Data Node is an abstract class that holds metadata related to the data it refers to.
    In particular, a data node holds the name, the scope, the owner identifier, the last
    edit date, and some additional properties of the data.<br/>
    A Data Node also contains information and methods needed to access the dataset. This
    information depends on the type of storage, and it is held by subclasses (such as
    SQL Data Node, CSV Data Node, ...).

    !!! note
        It is not recommended to instantiate subclasses of `DataNode` directly. Instead,
        you have two ways:

        1. Create a Scenario using the `create_scenario()^` function. Related data nodes
            will be created automatically. Please refer to the `Scenario^` class for more
            information.
        2. Configure a `DataNodeConfig^` with the various configuration methods form `Config^`
            and use the `create_global_data_node()^` function as illustrated in the following
            example.

    A data node's attributes are populated based on its configuration `DataNodeConfig^`.

    !!! Example

        ```python
        import taipy as tp
        from taipy import Config

        if __name__ == "__main__":
            # Configure a global data node
            dataset_cfg = Config.configure_data_node("my_dataset", scope=tp.Scope.GLOBAL)

            # Instantiate a global data node
            dataset = tp.create_global_data_node(dataset_cfg)

            # Retrieve the list of all data nodes
            all_data_nodes = tp.get_data_nodes()

            # Write the data
            dataset.write("Hello, World!")

            # Read the data
            print(dataset.read())
        ```
    """

    _ID_PREFIX = "DATANODE"
    __ID_SEPARATOR = "_"
    _logger = _TaipyLogger._get_logger()
    _REQUIRED_PROPERTIES: List[str] = []
    _MANAGER_NAME: str = "data"
    _PATH_KEY = "path"
    __EDIT_TIMEOUT = 30

    _TAIPY_PROPERTIES: Set[str] = set()

    id: DataNodeId
    """The unique identifier of the data node."""

    def __init__(
        self,
        config_id,
        scope: Scope = Scope(Scope.SCENARIO),  # noqa: B008
        id: Optional[DataNodeId] = None,
        owner_id: Optional[str] = None,
        parent_ids: Optional[Set[str]] = None,
        last_edit_date: Optional[datetime] = None,
        edits: Optional[List[Edit]] = None,
        version: Optional[str] = None,
        validity_period: Optional[timedelta] = None,
        edit_in_progress: bool = False,
        editor_id: Optional[str] = None,
        editor_expiration_date: Optional[datetime] = None,
        **kwargs,
    ) -> None:
        self._config_id = _validate_id(config_id)
        self.id = id or self._new_id(self._config_id)
        self._owner_id = owner_id
        self._parent_ids = parent_ids or set()
        self._scope = scope
        self._last_edit_date: Optional[datetime] = last_edit_date
        self._edit_in_progress = edit_in_progress
        self._version = version or _VersionManagerFactory._build_manager()._get_latest_version()
        self._validity_period = validity_period
        self._editor_id: Optional[str] = editor_id
        self._editor_expiration_date: Optional[datetime] = editor_expiration_date

        # Track edits
        self._edits: List[Edit] = edits or []

        self._properties: _Properties = _Properties(self, **kwargs)

    def __eq__(self, other) -> bool:
        """Check if two data nodes are equal."""
        return isinstance(other, DataNode) and self.id == other.id

    def __ne__(self, other) -> bool:
        """Check if two data nodes are different."""
        return not self == other

    def __hash__(self) -> int:
        """Hash the data node."""
        return hash(self.id)

    def __getstate__(self) -> Dict[str, Any]:
        return vars(self)

    def __setstate__(self, state) -> None:
        vars(self).update(state)

    def __getitem__(self, item) -> Any:
        data = self._read()
        return _FilterDataNode._filter_by_key(data, item)

    @property
    def config_id(self) -> str:
        """Identifier of the data node configuration. It must be a valid Python identifier."""
        return self._config_id

    @property
    def owner_id(self) -> Optional[str]:
        """The identifier of the owner (sequence_id, scenario_id, cycle_id) or None."""
        return self._owner_id

    @property  # type: ignore
    @_self_reload(_MANAGER_NAME)
    def parent_ids(self) -> Set[str]:
        """The set of identifiers of the parent tasks."""
        return self._parent_ids

    @property  # type: ignore
    @_self_reload(_MANAGER_NAME)
    def edits(self) -> List[Edit]:
        """The list of Edits.

        The list of Edits (an alias for dict) containing metadata about each
        data edition including but not limited to:
            <ul><li>timestamp: The time instant of the writing </li>
            <li>comments: Representation of a free text to explain or comment on a data change</li>
            <li>job_id: Only populated when the data node is written by a task execution and
                corresponds to the job's id.</li></ul>
        Additional metadata related to the edition made to the data node can also be provided in Edits.
        """
        return self._edits

    @property  # type: ignore
    @_self_reload(_MANAGER_NAME)
    def last_edit_date(self) -> Optional[datetime]:
        """The date and time of the last modification."""
        last_modified_datetime = self._get_last_modified_datetime(self._properties.get(self._PATH_KEY, None))
        if last_modified_datetime and last_modified_datetime > self._last_edit_date: # type: ignore
            return last_modified_datetime
        else:
            return self._last_edit_date

    @last_edit_date.setter  # type: ignore
    @_update_ready_for_reading
    @_self_setter(_MANAGER_NAME)
    def last_edit_date(self, val):
        self._last_edit_date = val

    @property  # type: ignore
    @_self_reload(_MANAGER_NAME)
    def scope(self) -> Scope:
        """The data node scope."""
        return self._scope

    @scope.setter  # type: ignore
    @_self_setter(_MANAGER_NAME)
    def scope(self, val):
        self._scope = val

    @property  # type: ignore
    @_self_reload(_MANAGER_NAME)
    def validity_period(self) -> Optional[timedelta]:
        """The duration since the last edit date for which the data node is considered up-to-date.

        The duration implemented as a timedelta since the last edit date for which the data node
        can be considered up-to-date. Once the validity period has passed, the data node is
        considered stale and relevant tasks will run even if they are skippable (see the
        Task orchestration page of the user manual for more details).

        If _validity_period_ is set to `None`, the data node is always up-to-date.
        """
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
    def name(self) -> Optional[str]:
        """A human-readable name of the data node."""
        return self.properties.get("name")

    @name.setter  # type: ignore
    def name(self, val):
        self.properties["name"] = val

    @property
    def version(self) -> str:
        """The string indicates the application version of the data node to instantiate.

        If not provided, the current version is used.
        """
        return self._version

    @property  # type: ignore
    @_self_reload(_MANAGER_NAME)
    def edit_in_progress(self) -> bool:
        """True if the data node is locked for modification. False otherwise."""
        return self._edit_in_progress

    @edit_in_progress.setter  # type: ignore
    @_update_ready_for_reading
    @_self_setter(_MANAGER_NAME)
    def edit_in_progress(self, val):
        self._edit_in_progress = val

    @property  # type: ignore
    @_self_reload(_MANAGER_NAME)
    def editor_id(self) -> Optional[str]:
        """The identifier of the user who is currently editing the data node."""
        return self._editor_id

    @editor_id.setter  # type: ignore
    @_self_setter(_MANAGER_NAME)
    def editor_id(self, val):
        self._editor_id = val

    @property  # type: ignore
    @_self_reload(_MANAGER_NAME)
    def editor_expiration_date(self) -> Optional[datetime]:
        """The expiration date of the editor lock."""
        return self._editor_expiration_date

    @editor_expiration_date.setter  # type: ignore
    @_self_setter(_MANAGER_NAME)
    def editor_expiration_date(self, val):
        self._editor_expiration_date = val

    @property  # type: ignore
    @_self_reload(_MANAGER_NAME)
    def job_ids(self) -> List[JobId]:
        """List of the jobs having edited this data node."""
        return [edit.get("job_id") for edit in self.edits if edit.get("job_id")]

    @property
    def properties(self):
        """Dictionary of custom properties."""
        self._properties = _Reloader()._reload(self._MANAGER_NAME, self)._properties
        return self._properties

    @property  # type: ignore
    @_self_reload(_MANAGER_NAME)
    def is_ready_for_reading(self) -> bool:
        """Indicate if this data node is ready for reading.

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
    def is_valid(self) -> bool:
        """Indicate if this data node is valid.

        False if the data ever been written or the expiration date has passed.<br/>
        True otherwise.
        """
        if not self._last_edit_date:
            # Never been written so it is not valid
            return False
        if not self._validity_period:
            # No validity period and has already been written, so it is valid
            return True
        if datetime.now() > self.expiration_date:
            # expiration_date has been passed
            return False
        return True

    @property
    def is_up_to_date(self) -> bool:
        """Indicate if this data node is up-to-date.

        False if a preceding data node has been updated before the selected data node
        or the selected data is invalid.<br/>
        True otherwise.
        """
        if self.is_valid:
            from ..scenario.scenario import Scenario
            from ..taipy import get_parents

            parent_scenarios: Set[Scenario] = get_parents(self)["scenario"]  # type: ignore
            for parent_scenario in parent_scenarios:
                for ancestor_node in nx.ancestors(parent_scenario._build_dag(), self):
                    if (
                        isinstance(ancestor_node, DataNode)
                        and ancestor_node.last_edit_date
                        and ancestor_node.last_edit_date > self.last_edit_date
                    ):
                        return False
            return True
        return False

    @classmethod
    @abstractmethod
    def storage_type(cls) -> str:
        """The storage type of the data node.

        Each subclass must implement this method exposing the data node storage type.
        """
        raise NotImplementedError

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
            self._logger.warning(
                f"Data node {self.id} from config {self.config_id} is being read but has never been written."
            )
            return None

    def append(self, data, job_id: Optional[JobId] = None, **kwargs: Dict[str, Any]):
        """Append some data to this data node.

        Parameters:
            data (Any): The data to write to this data node.
            job_id (JobId): An optional identifier of the writer.
            **kwargs (dict[str, any]): Extra information to attach to the edit document
                corresponding to this write.
        """
        from ._data_manager_factory import _DataManagerFactory

        self._append(data)
        self.track_edit(job_id=job_id, **kwargs)
        self.unlock_edit()
        _DataManagerFactory._build_manager()._set(self)

    def write(self, data, job_id: Optional[JobId] = None, **kwargs: Dict[str, Any]):
        """Write some data to this data node.

        Parameters:
            data (Any): The data to write to this data node.
            job_id (JobId): An optional identifier of the writer.
            **kwargs (dict[str, any]): Extra information to attach to the edit document
                corresponding to this write.
        """
        from ._data_manager_factory import _DataManagerFactory

        self._write(data)
        self.track_edit(job_id=job_id, **kwargs)
        self.unlock_edit()
        _DataManagerFactory._build_manager()._set(self)

    def track_edit(self, **options):
        """Creates and adds a new entry in the edits attribute without writing the data.

        Parameters:
            options (dict[str, any]): track `timestamp`, `comments`, `job_id`. The others are user-custom, users can
                use options to attach any information to an external edit of a data node.
        """
        edit = {k: v for k, v in options.items() if v is not None}
        if "timestamp" not in edit:
            edit["timestamp"] = (
                self._get_last_modified_datetime(self._properties.get(self._PATH_KEY, None)) or datetime.now()
            )
        self.last_edit_date = edit.get("timestamp")
        self._edits.append(edit)

    def lock_edit(self, editor_id: Optional[str] = None):
        """Lock the data node modification.

        Note:
            The data node can be unlocked with the method `(DataNode.)unlock_edit()^`.

        Parameters:
            editor_id (Optional[str]): The editor's identifier.
        """
        if editor_id:
            if (
                self.edit_in_progress
                and self.editor_id != editor_id
                and self.editor_expiration_date
                and self.editor_expiration_date > datetime.now()
            ):
                raise DataNodeIsBeingEdited(self.id, self._editor_id)
            self.editor_id = editor_id  # type: ignore
            self.editor_expiration_date = datetime.now() + timedelta(minutes=self.__EDIT_TIMEOUT)  # type: ignore
        else:
            self.editor_id = None  # type: ignore
            self.editor_expiration_date = None  # type: ignore
        self.edit_in_progress = True  # type: ignore

    def unlock_edit(self, editor_id: Optional[str] = None):
        """Unlocks the data node modification.

        Note:
            The data node can be locked with the method `(DataNode.)lock_edit()^`.

        Parameters:
            editor_id (Optional[str]): The editor's identifier.
        """
        if (
            editor_id
            and self.editor_id != editor_id
            and self.editor_expiration_date
            and self.editor_expiration_date > datetime.now()
        ):
            raise DataNodeIsBeingEdited(self.id, self._editor_id)

        self.editor_id = None
        self.editor_expiration_date = None
        self.edit_in_progress = False

    def filter(self, operators: Union[List, Tuple], join_operator=JoinOperator.AND) -> Any:
        """Read and filter the data referenced by this data node.

        The data is filtered by the provided list of 3-tuples (key, value, `Operator^`).

        If multiple filter operators are provided, filtered data will be joined based on the
        join operator (*AND* or *OR*).

        Parameters:
            operators (Union[List[Tuple], Tuple]): A 3-element tuple or a list of 3-element tuples,
                each is in the form of (key, value, `Operator^`).
            join_operator (JoinOperator^): The operator used to join the multiple filter
                3-tuples.

        Returns:
            The filtered data.

        Raises:
            NotImplementedError: If the data type is not supported.
        """
        data = self._read()
        return _FilterDataNode._filter(data, operators, join_operator)

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

    def get_parents(self) -> Dict[str, Set[_Entity]]:
        """Get all parents of this data node.

        Returns:
            The dictionary of all parent entities.
                They are grouped by their type (Scenario^, Sequences^, or tasks^) so each key corresponds
                to a level of the parents and the value is a set of the parent entities.
                An empty dictionary is returned if the entity does not have parents.
        """
        from ... import core as tp

        return tp.get_parents(self)

    def get_last_edit(self) -> Optional[Edit]:
        """Get last `Edit` of this data node.

        Returns:
            None if there has been no `Edit` on this data node.
        """
        return self._edits[-1] if self._edits else None

    @abstractmethod
    def _read(self):
        raise NotImplementedError

    def _append(self, data):
        raise NotImplementedError

    @abstractmethod
    def _write(self, data):
        raise NotImplementedError

    @staticmethod
    def _new_id(config_id: str) -> DataNodeId:
        """Generate a unique datanode identifier."""
        return DataNodeId(
            DataNode.__ID_SEPARATOR.join([DataNode._ID_PREFIX, _validate_id(config_id), str(uuid.uuid4())])
        )

    def _get_user_properties(self) -> Dict[str, Any]:
        """Get user properties."""
        return {key: value for key, value in self.properties.items() if key not in self._TAIPY_PROPERTIES}

    @classmethod
    def _get_last_modified_datetime(cls, path: Optional[str] = None) -> Optional[datetime]:
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

    @staticmethod
    def _class_map():
        def all_subclasses(cls):
            subclasses = set(cls.__subclasses__())
            for s in cls.__subclasses__():
                subclasses.update(all_subclasses(s))
            return subclasses

        class_map = {}
        for c in all_subclasses(DataNode):
            try:
                if c.storage_type() is not None:
                    class_map[c.storage_type()] = c
            except NotImplementedError:
                pass

        return class_map


@_make_event.register(DataNode)
def _make_event_for_datanode(
    data_node: DataNode,
    operation: EventOperation,
    /,
    attribute_name: Optional[str] = None,
    attribute_value: Optional[Any] = None,
    **kwargs,
) -> Event:
    metadata = {"config_id": data_node.config_id, "version": data_node._version, **kwargs}
    return Event(
        entity_type=EventEntityType.DATA_NODE,
        entity_id=data_node.id,
        operation=operation,
        attribute_name=attribute_name,
        attribute_value=attribute_value,
        metadata=metadata,
    )
