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
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Set, Union

import networkx as nx

from taipy.common.config.common._validate_id import _validate_id

from .._entity._entity import _Entity
from .._entity._labeled import _Labeled
from .._entity._properties import _Properties
from .._entity._reload import _Reloader, _self_reload, _self_setter
from .._entity.submittable import Submittable
from .._version._version_manager_factory import _VersionManagerFactory
from ..common._listattributes import _ListAttributes
from ..common._utils import _Subscriber
from ..cycle.cycle import Cycle
from ..data.data_node import DataNode
from ..data.data_node_id import DataNodeId
from ..exceptions.exceptions import (
    AttributeKeyAlreadyExisted,
    InvalidSequence,
    NonExistingDataNode,
    NonExistingSequence,
    NonExistingTask,
    SequenceAlreadyExists,
    SequenceTaskDoesNotExistInScenario,
)
from ..job.job import Job
from ..notification import Event, EventEntityType, EventOperation, Notifier, _make_event
from ..reason import ReasonCollection
from ..sequence.sequence import Sequence
from ..submission.submission import Submission
from ..task.task import Task
from ..task.task_id import TaskId
from .scenario_id import ScenarioId


class Scenario(_Entity, Submittable, _Labeled):
    """Instance of a Business case to solve.

    A scenario holds a set of tasks (instances of `Task^` class) to submit for execution in order
    to solve the Business case. Each task can be connected to some data nodes as input or output
    forming an execution graph. The scenario can be submitted for execution, and the tasks will
    be orchestrated to solve the Business case.<br>
    A scenario also holds a set of additional data nodes (instances of `DataNode^` class) for
    extra data related to the scenario.

    !!! note

        It is not recommended to instantiate a `Scenario` directly. Instead, it should be
        created with the `create_scenario()^` function.

    ??? Example

        ```python
        import taipy as tp
        from taipy import Config

        def by_two(x: int):
            return x * 2

        if __name__ == "__main__":
            # Configure scenarios
            input_cfg = Config.configure_data_node("my_input")
            result_cfg = Config.configure_data_node("my_result")
            task_cfg = Config.configure_task("my_double", function=by_two, input=input_cfg, output=result_cfg)
            scenario_cfg = Config.configure_scenario("my_scenario", task_configs=[task_cfg])

            # Create a new scenario from the configuration
            scenario = tp.create_scenario(scenario_cfg)

            # Write the input data and submit the scenario
            scenario.my_input.write(3)
            scenario.submit()

            # Read the result
            print(scenario.my_result.read())  # Output: 6

            # Retrieve all scenarios
            all_scenarios = tp.get_scenarios()
        ```
    """

    _ID_PREFIX = "SCENARIO"
    _MANAGER_NAME = "scenario"
    _MIGRATED_SEQUENCES_KEY = "sequences"
    __SEPARATOR = "_"
    _SEQUENCE_TASKS_KEY = "tasks"
    _SEQUENCE_PROPERTIES_KEY = "properties"
    _SEQUENCE_SUBSCRIBERS_KEY = "subscribers"
    __CHECK_INIT_DONE_ATTR_NAME = "_init_done"

    id: ScenarioId
    """The unique identifier of this scenario."""

    def __init__(
        self,
        config_id: str,
        tasks: Optional[Union[Set[TaskId], Set[Task]]],
        properties: Dict[str, Any],
        additional_data_nodes: Optional[Union[Set[DataNodeId], Set[DataNode]]] = None,
        scenario_id: Optional[ScenarioId] = None,
        creation_date: Optional[datetime] = None,
        is_primary: bool = False,
        cycle: Optional[Cycle] = None,
        subscribers: Optional[List[_Subscriber]] = None,
        tags: Optional[Set[str]] = None,
        version: str = None,
        sequences: Optional[Dict[str, Dict]] = None,
    ):
        self._config_id = _validate_id(config_id)
        self.id: ScenarioId = scenario_id or self._new_id(self.config_id)
        super().__init__(self.id, subscribers or [])

        self._tasks: Union[Set[TaskId], Set[Task], Set] = tasks or set()
        self._additional_data_nodes: Union[Set[DataNodeId], Set[DataNode], Set] = additional_data_nodes or set()

        self._creation_date = creation_date or datetime.now()
        self._cycle = cycle
        self._primary_scenario = is_primary
        self._tags = tags or set()
        self._properties = _Properties(self, **properties)
        self._sequences: Dict[str, Dict] = sequences or {}

        _scenario_task_ids = {task.id if isinstance(task, Task) else task for task in self._tasks}
        for sequence_name, sequence_data in self._sequences.items():
            sequence_task_ids = {task.id if isinstance(task, Task) else task for task in sequence_data.get("tasks", [])}
            self.__check_sequence_tasks_exist_in_scenario_tasks(
                sequence_name, sequence_task_ids, self.id, _scenario_task_ids
            )

        self._version = version or _VersionManagerFactory._build_manager()._get_latest_version()
        self._init_done = True

    def __getstate__(self):
        return self.id

    def __setstate__(self, id) -> None:
        from ... import core as tp

        sc = tp.get(id)
        self.__dict__ = sc.__dict__

    def __hash__(self) -> int:
        """Return the hash of the scenario."""
        return hash(self.id)

    def __eq__(self, other) -> bool:
        """Check if the scenario is equal to another scenario."""
        return isinstance(other, Scenario) and self.id == other.id

    def __setattr__(self, name: str, value: Any) -> None:
        if self.__CHECK_INIT_DONE_ATTR_NAME not in dir(self) or name in dir(self):
            return super().__setattr__(name, value)
        else:
            try:
                self.__getattr__(name)
                raise AttributeKeyAlreadyExisted(name)
            except AttributeError:
                return super().__setattr__(name, value)

    def __getattr__(self, attribute_name: str) -> Union[Sequence, Task, DataNode]:
        """Get a scenario attribute by its name.

        The attribute can be a sequence, a task, or a data node.

        Parameters:
            attribute_name (str): The name of the attribute to get.

        Returns:
            The attribute with the given name.

        Raises:
            AttributeError: If the attribute is not found.
        """
        protected_attribute_name = _validate_id(attribute_name)
        sequences = self._get_sequences()
        if protected_attribute_name in sequences:
            return sequences[protected_attribute_name]
        tasks = self.__get_tasks()
        if protected_attribute_name in tasks:
            return tasks[protected_attribute_name]
        data_nodes = self.__get_data_nodes()
        if protected_attribute_name in data_nodes:
            return data_nodes[protected_attribute_name]

        raise AttributeError(f"{attribute_name} is not an attribute of scenario {self.id}")

    @property
    def config_id(self) -> str:
        """The identifier of the `ScenarioConfig^`."""
        return self._config_id

    @property  # type: ignore
    @_self_reload(_MANAGER_NAME)
    def sequences(self) -> Dict[str, Sequence]:
        """The dictionary of the scenario's sequences.

        The sequences are subsets of tasks that can be submitted together independently of
        the rest of the scenario's tasks."""
        return self._get_sequences()

    @sequences.setter  # type: ignore
    @_self_setter(_MANAGER_NAME)
    def sequences(
        self, sequences: Dict[str, Dict[str, Union[List[Task], List[TaskId], _ListAttributes, List[_Subscriber], Dict]]]
    ) -> None:
        self._sequences = sequences
        actual_sequences = self._get_sequences()
        for sequence_name in sequences.keys():
            if not actual_sequences[sequence_name]._is_consistent():
                raise InvalidSequence(actual_sequences[sequence_name].id)

    @property  # type: ignore
    @_self_reload(_MANAGER_NAME)
    def tasks(self) -> Dict[str, Task]:
        """The dictionary of the scenario's tasks."""
        return self.__get_tasks()

    @tasks.setter  # type: ignore
    @_self_setter(_MANAGER_NAME)
    def tasks(self, val: Union[Set[TaskId], Set[Task]]) -> None:
        self._tasks = set(val)

    @property  # type: ignore
    @_self_reload(_MANAGER_NAME)
    def additional_data_nodes(self) -> Dict[str, DataNode]:
        """The dictionary of the scenario's additional data nodes.

        Additional data nodes are data nodes that are not part of the
        scenario's graph but are used to store extra data. They are not
        connected to the scenario's tasks."""
        return self.__get_additional_data_nodes()

    @additional_data_nodes.setter  # type: ignore
    @_self_setter(_MANAGER_NAME)
    def additional_data_nodes(self, val: Union[Set[TaskId], Set[DataNode]]) -> None:
        self._additional_data_nodes = set(val)

    @property  # type: ignore
    @_self_reload(_MANAGER_NAME)
    def data_nodes(self) -> Dict[str, DataNode]:
        """The dictionary of the scenario's data nodes."""
        return self.__get_data_nodes()

    @property  # type: ignore
    @_self_reload(_MANAGER_NAME)
    def creation_date(self) -> datetime:
        """The date and time of the scenario's creation."""
        return self._creation_date

    @creation_date.setter  # type: ignore
    @_self_setter(_MANAGER_NAME)
    def creation_date(self, val) -> None:
        self._creation_date = val

    @property  # type: ignore
    @_self_reload(_MANAGER_NAME)
    def cycle(self) -> Optional[Cycle]:
        """The cycle of the scenario"""
        return self._cycle

    @cycle.setter  # type: ignore
    @_self_setter(_MANAGER_NAME)
    def cycle(self, val) -> None:
        self._cycle = val

    @property  # type: ignore
    @_self_reload(_MANAGER_NAME)
    def is_primary(self) -> bool:
        """True if the scenario is the primary of its cycle. False otherwise."""
        return self._primary_scenario

    @is_primary.setter  # type: ignore
    @_self_setter(_MANAGER_NAME)
    def is_primary(self, val) -> None:
        self._primary_scenario = val

    @property  # type: ignore
    @_self_reload(_MANAGER_NAME)
    def subscribers(self) -> _ListAttributes:
        """The list of callbacks to be called on `Job^`'s status change."""
        return self._subscribers

    @subscribers.setter  # type: ignore
    @_self_setter(_MANAGER_NAME)
    def subscribers(self, val) -> None:
        self._subscribers = _ListAttributes(self, val)

    @property  # type: ignore
    @_self_reload(_MANAGER_NAME)
    def tags(self) -> Set[str]:
        """The set of scenario's tags."""
        return self._tags

    @tags.setter  # type: ignore
    @_self_setter(_MANAGER_NAME)
    def tags(self, val) -> None:
        self._tags = val or set()

    @property
    def version(self) -> str:
        """The application version of the scenario.

        The string indicates the application version of the scenario. If not
        provided, the latest version is used."""
        return self._version

    @property
    def owner_id(self) -> Optional[str]:
        """The identifier of the scenario cycle."""
        return self._cycle.id if self._cycle else None

    @property
    def properties(self) -> _Properties:
        """The dictionary of additional properties."""
        self._properties = _Reloader()._reload(self._MANAGER_NAME, self)._properties
        return self._properties

    @property  # type: ignore
    def name(self) -> Optional[str]:
        """The human-readable name of the scenario."""
        return self.properties.get("name")

    @name.setter  # type: ignore
    def name(self, val) -> None:
        self.properties["name"] = val

    def has_tag(self, tag: str) -> bool:
        """Indicate if the scenario has a given tag.

        Parameters:
            tag (str): The tag to search among the set of scenario's tags.

        Returns:
            True if the scenario has the tag given as parameter. False otherwise.
        """
        return tag in self.tags

    def subscribe(self, callback: Callable[[Scenario, Job], None], params: Optional[List[Any]] = None) -> None:
        """Subscribe a function to be called on `Job^` status change.

        The subscription is applied to all jobs created from the scenario's execution.

        Note:
            Notification will be available only for jobs created after this subscription.

        Parameters:
            callback (Callable[[Scenario^, Job^], None]): The callable function to be called
                on status change.
            params (Optional[List[Any]]): The parameters to be passed to the _callback_.
        """
        from ... import core as tp

        return tp.subscribe_scenario(callback, params, self)

    def unsubscribe(self, callback: Callable[[Scenario, Job], None], params: Optional[List[Any]] = None) -> None:
        """Unsubscribe a function that is called when the status of a `Job^` changes.

        Note:
            The function will continue to be called for ongoing jobs.

        Parameters:
            callback (Callable[[Scenario^, Job^], None]): The callable function to unsubscribe.
            params (Optional[List[Any]]): The parameters to be passed to the _callback_.
        """
        from ... import core as tp

        return tp.unsubscribe_scenario(callback, params, self)

    def submit(
        self,
        callbacks: Optional[List[Callable]] = None,
        force: bool = False,
        wait: bool = False,
        timeout: Optional[Union[float, int]] = None,
        **properties,
    ) -> Submission:
        """Submit this scenario for execution.

        All the `Task^`s of the scenario will be submitted for execution.

        Parameters:
            callbacks (List[Callable]): The list of callable functions to be called on status
                change.
            force (bool): Force execution even if the data nodes are in cache.
            wait (bool): Wait for the orchestrated jobs created from the scenario submission to be finished in
                asynchronous mode.
            timeout (Union[float, int]): The optional maximum number of seconds to wait for the jobs to be finished
                before returning.<br/>
                If not provided and *wait* is True, the function waits indefinitely.
            **properties (dict[str, any]): A keyworded variable length list of additional arguments.

        Returns:
            A `Submission^` containing the information of the submission.
        """
        from ._scenario_manager_factory import _ScenarioManagerFactory

        return _ScenarioManagerFactory._build_manager()._submit(self, callbacks, force, wait, timeout, **properties)

    def set_primary(self) -> None:
        """Promote the scenario as the primary scenario of its cycle.

        If the cycle already has a primary scenario, it will be demoted, and it will no longer
        be primary for the cycle.
        """
        from ... import core as tp

        return tp.set_primary(self)

    def add_tag(self, tag: str) -> None:
        """Add a tag to this scenario.

        If the scenario's cycle already have another scenario tagged with _tag_ the other
        scenario will be untagged.

        Parameters:
            tag (str): The tag to add to this scenario.
        """
        from ... import core as tp

        return tp.tag(self, tag)

    def remove_tag(self, tag: str) -> None:
        """Remove a tag from this scenario.

        Parameters:
            tag (str): The tag to remove from the set of the scenario's tags.
        """
        from ... import core as tp

        return tp.untag(self, tag)

    def is_deletable(self) -> ReasonCollection:
        """Indicate if the scenario can be deleted.

        Returns:
            True if the scenario can be deleted. False otherwise.
        """
        from ... import core as tp

        return tp.is_deletable(self)

    def get_label(self) -> str:
        """Returns the scenario simple label prefixed by its owner label.

        Returns:
            The label of the scenario as a string.
        """
        return self._get_label()

    def get_simple_label(self) -> str:
        """Returns the scenario simple label.

        Returns:
            The simple label of the scenario as a string.
        """
        return self._get_simple_label()

    def add_sequence(
        self,
        name: str,
        tasks: Union[List[Task], List[TaskId]],
        properties: Optional[Dict] = None,
        subscribers: Optional[List[_Subscriber]] = None,
    ) -> None:
        """Add a sequence to the scenario.

        Parameters:
            name (str): The name of the sequence.
            tasks (Union[List[Task], List[TaskId]]): The list of scenario's tasks to add to the sequence.
            properties (Optional[Dict]): The optional properties of the sequence.
            subscribers (Optional[List[_Subscriber]]): The optional list of callbacks to be called on
                `Job^`'s status change.

        Raises:
            SequenceTaskDoesNotExistInScenario^: If a task in the sequence does not exist in the scenario.
            SequenceAlreadyExists^: If a sequence with the same name already exists in the scenario.
        """
        if name in self.sequences:
            raise SequenceAlreadyExists(name, self.id)
        seq = self._set_sequence(name, tasks, properties, subscribers)
        Notifier.publish(_make_event(seq, EventOperation.CREATION))

    def update_sequence(
        self,
        name: str,
        tasks: Union[List[Task], List[TaskId]],
        properties: Optional[Dict] = None,
        subscribers: Optional[List[_Subscriber]] = None,
    ) -> None:
        """Update an existing sequence.

        Parameters:
            name (str): The name of the sequence to update.
            tasks (Union[List[Task], List[TaskId]]): The new list of scenario's tasks.
            properties (Optional[Dict]): The new properties of the sequence.
            subscribers (Optional[List[_Subscriber]]): The new list of callbacks to be called on `Job^`'s status change.

        Raises:
            SequenceTaskDoesNotExistInScenario^: If a task in the list does not exist in the scenario.
            SequenceAlreadyExists^: If a sequence with the same name already exists in the scenario.
        """
        if name not in self.sequences:
            raise NonExistingSequence(name, self.id)
        seq = self._set_sequence(name, tasks, properties, subscribers)
        Notifier.publish(_make_event(seq, EventOperation.UPDATE))

    def add_sequences(self, sequences: Dict[str, Union[List[Task], List[TaskId]]]) -> None:
        """Add multiple sequences to the scenario.

        Note:
            To provide properties and subscribers for the sequences, use `Scenario.add_sequence^` instead.

        Parameters:
            sequences (Dict[str, Union[List[Task], List[TaskId]]]):
                A dictionary containing sequences to add. Each key is a sequence name, and the value must
                be a list of the scenario tasks.

        Raises:
            SequenceTaskDoesNotExistInScenario^: If a task in the sequence does not exist in the scenario.
        """
        _scenario = _Reloader()._reload(self._MANAGER_NAME, self)
        _sc_task_ids = {task.id if isinstance(task, Task) else task for task in _scenario._tasks}
        for name, tasks in sequences.items():
            _seq_task_ids: Set[TaskId] = {task.id if isinstance(task, Task) else task for task in tasks}
            self.__check_sequence_tasks_exist_in_scenario_tasks(name, _seq_task_ids, self.id, _sc_task_ids)
        # Need to parse twice the sequences to avoid adding some sequences and not others in case of exception
        for name, tasks in sequences.items():
            self.add_sequence(name, tasks)

    def remove_sequence(self, name: str) -> None:
        """Remove a sequence from the scenario.

        Parameters:
            name (str): The name of the sequence to remove.
        """
        seq_id = self.sequences[name].id
        _sequences = _Reloader()._reload(self._MANAGER_NAME, self)._sequences
        _sequences.pop(name)
        self.sequences = _sequences  # type: ignore
        Notifier.publish(Event(EventEntityType.SEQUENCE, EventOperation.DELETION, entity_id=seq_id))

    def remove_sequences(self, sequence_names: List[str]) -> None:
        """Remove multiple sequences from the scenario.

        Parameters:
            sequence_names (List[str]): A list of sequence names to remove.
        """
        _sequences = _Reloader()._reload(self._MANAGER_NAME, self)._sequences
        for sequence_name in sequence_names:
            seq_id = self.sequences[sequence_name].id
            _sequences.pop(sequence_name)
            Notifier.publish(
                Event(
                    EventEntityType.SEQUENCE,
                    EventOperation.DELETION,
                    entity_id=seq_id,
                )
            )
        self.sequences = _sequences  # type: ignore

    def rename_sequence(self, old_name, new_name) -> None:
        """Rename a scenario sequence.

        Parameters:
            old_name (str): The current name of the sequence to rename.
            new_name (str): The new name of the sequence.

        Raises:
            SequenceAlreadyExists^: If a sequence with the same name already exists in the scenario.
        """
        if old_name == new_name:
            return
        if new_name in self.sequences:
            raise SequenceAlreadyExists(new_name, self.id)
        self._sequences[new_name] = self._sequences[old_name]
        del self._sequences[old_name]
        self.sequences = self._sequences  # type: ignore
        Notifier.publish(
            Event(
                EventEntityType.SCENARIO,
                EventOperation.UPDATE,
                entity_id=self.id,
                attribute_name="sequences",
                attribute_value=self._sequences,
            )
        )

    @staticmethod
    def _new_id(config_id: str) -> ScenarioId:
        """Generate a unique scenario identifier."""
        return ScenarioId(Scenario.__SEPARATOR.join([Scenario._ID_PREFIX, _validate_id(config_id), str(uuid.uuid4())]))

    def _is_consistent(self) -> bool:
        """Check if the scenario is consistent."""
        dag = self._build_dag()
        if dag.number_of_nodes() == 0:
            return True
        if not nx.is_directed_acyclic_graph(dag):
            return False
        for left_node, right_node in dag.edges:
            if (isinstance(left_node, DataNode) and isinstance(right_node, Task)) or (
                isinstance(left_node, Task) and isinstance(right_node, DataNode)
            ):
                continue
            return False
        return True

    def _add_tag(self, tag: str) -> None:
        self._tags = _Reloader()._reload("scenario", self)._tags
        self._tags.add(tag)

    def _remove_tag(self, tag: str) -> None:
        self._tags = _Reloader()._reload("scenario", self)._tags
        if self.has_tag(tag):
            self._tags.remove(tag)

    def _get_set_of_tasks(self) -> Set[Task]:
        return set(self.tasks.values())

    def __get_data_nodes(self) -> Dict[str, DataNode]:
        data_nodes_dict = self.__get_additional_data_nodes()
        for _, task in self.__get_tasks().items():
            data_nodes_dict.update(task.data_nodes)
        return data_nodes_dict

    def __get_additional_data_nodes(self):
        from ..data._data_manager_factory import _DataManagerFactory

        additional_data_nodes = {}
        data_manager = _DataManagerFactory._build_manager()

        for dn_or_id in self._additional_data_nodes:
            dn = data_manager._get(dn_or_id, dn_or_id)

            if not isinstance(dn, DataNode):
                raise NonExistingDataNode(dn_or_id)
            additional_data_nodes[dn.config_id] = dn
        return additional_data_nodes

    def __get_tasks(self) -> Dict[str, Task]:
        from ..task._task_manager_factory import _TaskManagerFactory

        _tasks = {}
        task_manager = _TaskManagerFactory._build_manager()

        for task_or_id in self._tasks:
            t = task_manager._get(task_or_id, task_or_id)

            if not isinstance(t, Task):
                raise NonExistingTask(task_or_id)
            _tasks[t.config_id] = t
        return _tasks

    @staticmethod
    def __check_sequence_tasks_exist_in_scenario_tasks(
        sequence_name: str, sequence_task_ids: Set[TaskId], scenario_id: ScenarioId, scenario_task_ids: Set[TaskId]
    ):
        non_existing_sequence_task_ids_in_scenario = set()
        for sequence_task_id in sequence_task_ids:
            if sequence_task_id not in scenario_task_ids:
                non_existing_sequence_task_ids_in_scenario.add(sequence_task_id)
        if len(non_existing_sequence_task_ids_in_scenario) > 0:
            raise SequenceTaskDoesNotExistInScenario(
                list(non_existing_sequence_task_ids_in_scenario), sequence_name, scenario_id
            )

    def _get_sequences(self) -> Dict[str, Sequence]:
        _sequences = {}

        from ..sequence._sequence_manager_factory import _SequenceManagerFactory

        sequence_manager = _SequenceManagerFactory._build_manager()

        for sequence_name, sequence_data in self._sequences.items():
            sequence = sequence_manager._build_sequence(
                sequence_name,
                sequence_data.get(self._SEQUENCE_TASKS_KEY, []),
                sequence_data.get(self._SEQUENCE_SUBSCRIBERS_KEY, []),
                sequence_data.get(self._SEQUENCE_PROPERTIES_KEY, {}),
                self.id,
                self.version,
            )
            if not isinstance(sequence, Sequence):
                raise NonExistingSequence(sequence_name, self.id)
            _sequences[sequence_name] = sequence
        return _sequences

    def _set_sequence(
        self,
        name: str,
        tasks: Union[List[Task], List[TaskId]],
        properties: Optional[Dict] = None,
        subscribers: Optional[List[_Subscriber]] = None,
    ) -> Sequence:
        _scenario = _Reloader()._reload(self._MANAGER_NAME, self)
        _scenario_task_ids = {task.id if isinstance(task, Task) else task for task in _scenario._tasks}
        _sequence_task_ids: Set[TaskId] = {task.id if isinstance(task, Task) else task for task in tasks}
        self.__check_sequence_tasks_exist_in_scenario_tasks(name, _sequence_task_ids, self.id, _scenario_task_ids)

        from taipy.core.sequence._sequence_manager_factory import _SequenceManagerFactory

        seq_manager = _SequenceManagerFactory._build_manager()
        seq = seq_manager._create(name, tasks, subscribers or [], properties or {}, self.id, self.version)

        _sequences = _Reloader()._reload(self._MANAGER_NAME, self)._sequences
        _sequences.update(
            {
                name: {
                    self._SEQUENCE_TASKS_KEY: tasks,
                    self._SEQUENCE_PROPERTIES_KEY: properties or {},
                    self._SEQUENCE_SUBSCRIBERS_KEY: subscribers or [],
                }
            }
        )
        self.sequences = _sequences  # type: ignore
        return seq


@_make_event.register(Scenario)
def _make_event_for_scenario(
    scenario: Scenario,
    operation: EventOperation,
    /,
    attribute_name: Optional[str] = None,
    attribute_value: Optional[Any] = None,
    **kwargs,
) -> Event:
    metadata = {"config_id": scenario.config_id, "version": scenario._version, **kwargs}
    return Event(
        entity_type=EventEntityType.SCENARIO,
        entity_id=scenario.id,
        operation=operation,
        attribute_name=attribute_name,
        attribute_value=attribute_value,
        metadata=metadata,
    )
