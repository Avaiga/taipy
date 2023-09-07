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

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional, Set, Union

import networkx as nx

from taipy.config.common._template_handler import _TemplateHandler as _tpl
from taipy.config.common._validate_id import _validate_id

from .._entity._entity import _Entity
from .._entity._labeled import _Labeled
from .._entity._properties import _Properties
from .._entity._reload import _Reloader, _self_reload, _self_setter
from .._entity.submittable import Submittable
from .._version._version_manager_factory import _VersionManagerFactory
from ..common._listattributes import _ListAttributes
from ..common._utils import _Subscriber
from ..data.data_node import DataNode
from ..exceptions.exceptions import NonExistingTask
from ..job.job import Job
from ..task.task import Task
from ..task.task_id import TaskId
from .sequence_id import SequenceId


class Sequence(_Entity, Submittable, _Labeled):
    """List of `Task^`s and additional attributes representing a set of data processing
    elements connected as a direct acyclic graph.

    Attributes:
        properties (dict[str, Any]): A dictionary of additional properties.
        tasks (List[Task^]): The list of `Task`s.
        sequence_id (str): The Unique identifier of the sequence.
        owner_id (str):  The identifier of the owner (scenario_id, cycle_id) or None.
        parent_ids (Optional[Set[str]]): The set of identifiers of the parent scenarios.
        version (str): The string indicates the application version of the sequence to instantiate. If not provided,
            the latest version is used.
    """

    _ID_PREFIX = "SEQUENCE"
    _SEPARATOR = "_"
    _MANAGER_NAME = "sequence"

    def __init__(
        self,
        properties: Dict[str, Any],
        tasks: Union[List[TaskId], List[Task], List[Union[TaskId, Task]]],
        sequence_id: SequenceId,
        owner_id: Optional[str] = None,
        parent_ids: Optional[Set[str]] = None,
        subscribers: Optional[List[_Subscriber]] = None,
        version: Optional[str] = None,
    ):
        super().__init__(subscribers)
        self.id: SequenceId = sequence_id
        self._tasks = tasks
        self.owner_id = owner_id
        self._parent_ids = parent_ids or set()
        self._properties = _Properties(self, **properties)
        self._version = version or _VersionManagerFactory._build_manager()._get_latest_version()

    @staticmethod
    def _new_id(sequence_name: str, scenario_id) -> SequenceId:
        return SequenceId(Sequence._SEPARATOR.join([Sequence._ID_PREFIX, _validate_id(sequence_name), scenario_id]))

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id

    def __getattr__(self, attribute_name):
        protected_attribute_name = _validate_id(attribute_name)
        if protected_attribute_name in self._properties:
            return _tpl._replace_templates(self._properties[protected_attribute_name])
        tasks = self._get_tasks()
        if protected_attribute_name in tasks:
            return tasks[protected_attribute_name]
        for task in tasks.values():
            if protected_attribute_name in task.input:
                return task.input[protected_attribute_name]
            if protected_attribute_name in task.output:
                return task.output[protected_attribute_name]
        raise AttributeError(f"{attribute_name} is not an attribute of sequence {self.id}")

    @property  # type: ignore
    @_self_reload(_MANAGER_NAME)
    def tasks(self) -> Dict[str, Task]:
        return self._get_tasks()

    @tasks.setter  # type: ignore
    @_self_setter(_MANAGER_NAME)
    def tasks(self, tasks: Union[List[TaskId], List[Task]]):
        self._tasks = tasks

    @property
    def data_nodes(self) -> Dict[str, DataNode]:
        data_nodes = {}
        list_data_nodes = [task.data_nodes for task in self._get_tasks().values()]
        for data_node in list_data_nodes:
            for k, v in data_node.items():
                data_nodes[k] = v
        return data_nodes

    @property
    def parent_ids(self):
        return self._parent_ids

    @property
    def version(self):
        return self._version

    @property
    def properties(self):
        self._properties = _Reloader()._reload("sequence", self)._properties
        return self._properties

    def _is_consistent(self) -> bool:
        dag = self._build_dag()
        if dag.number_of_nodes() == 0:
            return True
        if not nx.is_directed_acyclic_graph(dag):
            return False
        if not nx.is_weakly_connected(dag):
            return False
        for left_node, right_node in dag.edges:
            if (isinstance(left_node, DataNode) and isinstance(right_node, Task)) or (
                isinstance(left_node, Task) and isinstance(right_node, DataNode)
            ):
                continue
            return False
        return True

    def _get_tasks(self) -> Dict[str, Task]:
        from ..task._task_manager_factory import _TaskManagerFactory

        tasks = {}
        task_manager = _TaskManagerFactory._build_manager()
        for task_or_id in self._tasks:
            t = task_manager._get(task_or_id, task_or_id)
            if not isinstance(t, Task):
                raise NonExistingTask(task_or_id)
            tasks[t.config_id] = t
        return tasks

    def _get_set_of_tasks(self) -> Set[Task]:
        from ..task._task_manager_factory import _TaskManagerFactory

        tasks = set()
        task_manager = _TaskManagerFactory._build_manager()
        for task_or_id in self._tasks:
            task = task_manager._get(task_or_id, task_or_id)
            if not isinstance(task, Task):
                raise NonExistingTask(task_or_id)
            tasks.add(task)
        return tasks

    @property  # type: ignore
    @_self_reload(_MANAGER_NAME)
    def subscribers(self):
        return self._subscribers

    @subscribers.setter  # type: ignore
    @_self_setter(_MANAGER_NAME)
    def subscribers(self, val):
        self._subscribers = _ListAttributes(self, val)

    def get_parents(self):
        """Get parents of the sequence entity"""
        from ... import core as tp

        return tp.get_parents(self)

    def subscribe(
        self,
        callback: Callable[[Sequence, Job], None],
        params: Optional[List[Any]] = None,
    ):
        """Subscribe a function to be called on `Job^` status change.
        The subscription is applied to all jobs created from the sequence's execution.

        Parameters:
            callback (Callable[[Sequence^, Job^], None]): The callable function to be called on
                status change.
            params (Optional[List[Any]]): The parameters to be passed to the _callback_.
        Note:
            Notification will be available only for jobs created after this subscription.
        """
        from ... import core as tp

        return tp.subscribe_sequence(callback, params, self)

    def unsubscribe(self, callback: Callable[[Sequence, Job], None], params: Optional[List[Any]] = None):
        """Unsubscribe a function that is called when the status of a `Job^` changes.

        Parameters:
            callback (Callable[[Sequence^, Job^], None]): The callable function to unsubscribe.
            params (Optional[List[Any]]): The parameters to be passed to the _callback_.
        Note:
            The function will continue to be called for ongoing jobs.
        """
        from ... import core as tp

        return tp.unsubscribe_sequence(callback, params, self)

    def submit(
        self,
        callbacks: Optional[List[Callable]] = None,
        force: bool = False,
        wait: bool = False,
        timeout: Optional[Union[float, int]] = None,
    ) -> List[Job]:
        """Submit the sequence for execution.

        All the `Task^`s of the sequence will be submitted for execution.

        Parameters:
            callbacks (List[Callable]): The list of callable functions to be called on status
                change.
            force (bool): Force execution even if the data nodes are in cache.
            wait (bool): Wait for the orchestrated jobs created from the sequence submission to be finished
                in asynchronous mode.
            timeout (Union[float, int]): The maximum number of seconds to wait for the jobs to be finished before
                returning.
        Returns:
            A list of created `Job^`s.
        """
        from ._sequence_manager_factory import _SequenceManagerFactory

        return _SequenceManagerFactory._build_manager()._submit(self, callbacks, force, wait, timeout)

    def get_label(self) -> str:
        """Returns the sequence simple label prefixed by its owner label.

        Returns:
            The label of the sequence as a string.
        """
        return self._get_label()

    def get_simple_label(self) -> str:
        """Returns the sequence simple label.

        Returns:
            The simple label of the sequence as a string.
        """
        return self._get_simple_label()
