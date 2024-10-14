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
from ..data.data_node import DataNode
from ..exceptions.exceptions import AttributeKeyAlreadyExisted, NonExistingTask
from ..job.job import Job
from ..notification.event import Event, EventEntityType, EventOperation, _make_event
from ..submission.submission import Submission
from ..task.task import Task
from ..task.task_id import TaskId
from .sequence_id import SequenceId


class Sequence(_Entity, Submittable, _Labeled):
    """A subset of scenario tasks grouped to be executed together independently of the others.

    A sequence is attached to a `Scenario^`. It represents a subset of its tasks that need to
    be executed together, independently of the other tasks in the scenario. They must form a
    connected subgraph of the scenario's task graph. A scenario can hold multiple sequences.

    For instance, in a typical machine learning scenario, we may have several sequences:
    a sequence dedicated to preprocessing and preparing data, a sequence for computing a
    training model, and a sequence dedicated to scoring.

    ??? Example

        Let's assume we have a scenario configuration modelling a manufacturer that is
        training an ML model, predicting sales forecasts, and finally, based on
        the forecasts, planning its production. Three task are configured and linked
        together through data nodes.

        ![sequences](../../../../img/sequences.svg){ align=left }

        First, the sales sequence (boxed in green in the picture) contains **training**
        and **predict** tasks. Second, a production sequence (boxed in dark gray in the
        picture) contains the **planning** task.

        This problem has been modeled in two sequences - one sequence for the forecasting
        part and one for the production planning part. As a consequence, the two algorithms
        can have two different life cycles. They can run independently, under different
        schedules. For example, one on a fixed schedule (e.g. every week) and one on demand,
        interactively triggered by end-users.

        ```python
        import taipy as tp
        from taipy import Config

        def training(history):
            ...

        def predict(model, month):
            ...

        def planning(forecast, capacity):
            ...

        if __name__ == "__main__":
            # Configure data nodes
            sales_history_cfg = Config.configure_csv_data_node("sales_history")
            trained_model_cfg = Config.configure_data_node("trained_model")
            current_month_cfg = Config.configure_data_node("current_month")
            forecasts_cfg = Config.configure_data_node("sales_predictions")
            capacity_cfg = Config.configure_data_node("capacity")
            production_orders_cfg = Config.configure_sql_data_node("production_orders")

            # Configure tasks and scenarios
            train_cfg = Config.configure_task("train", function=training,
                                              input=sales_history_cfg, output=trained_model_cfg)
            predict_cfg = Config.configure_task("predict", function=predict,
                                                input=[trained_model_cfg, current_month_cfg],
                                                output=forecasts_cfg)
            plan_cfg = Config.configure_task("planning", function=planning,
                                            input=[forecasts_cfg, capacity_cfg],
                                            output=production_orders_cfg)
            scenario_cfg = Config.configure_scenario("scenario", task_configs=[train_cfg, predict_cfg, plan_cfg])

            # Create a new scenario and sequences
            scenario = tp.create_scenario(scenario_cfg)
            scenario.add_sequence("sales_sequence", [train_cfg, predict_cfg])
            scenario.add_sequence("production_sequence", [plan_cfg])

            # Get all sequences
            all_sequences = tp.get_sequences()

            # Submit one sequence only
            tp.submit(scenario.sales_sequence)
        ```

    Note that the sequences are not necessarily disjoint and may share some tasks.
    """

    _ID_PREFIX = "SEQUENCE"
    _SEPARATOR = "_"
    _MANAGER_NAME = "sequence"
    __CHECK_INIT_DONE_ATTR_NAME = "_init_done"

    id: SequenceId
    """The unique identifier of the sequence."""

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
        self.id: SequenceId = sequence_id
        super().__init__(self.id, subscribers)
        self._tasks = tasks
        self._owner_id = owner_id
        self._parent_ids = parent_ids or set()
        self._properties = _Properties(self, **properties)
        self._version = version or _VersionManagerFactory._build_manager()._get_latest_version()
        self._init_done = True

    def __hash__(self) -> int:
        """Return the hash of the sequence."""
        return hash(self.id)

    def __eq__(self, other) -> bool:
        """Check if a sequence is equal to another sequence."""
        return isinstance(other, Sequence) and self.id == other.id

    def __setattr__(self, name: str, value: Any) -> None:
        if self.__CHECK_INIT_DONE_ATTR_NAME not in dir(self) or name in dir(self):
            return super().__setattr__(name, value)
        else:
            try:
                self.__getattr__(name)
                raise AttributeKeyAlreadyExisted(name)
            except AttributeError:
                return super().__setattr__(name, value)

    def __getattr__(self, attribute_name: str):
        """Get the attribute of the sequence.

        The attribute can be a task or a data node.

        Parameters:
            attribute_name (str): The attribute name.

        Returns:
            The attribute value.

        Raises:
            AttributeError: If the attribute is not found.

        """
        protected_attribute_name = _validate_id(attribute_name)
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
        """The dictionary of tasks used by the sequence."""
        return self._get_tasks()

    @tasks.setter  # type: ignore
    @_self_setter(_MANAGER_NAME)
    def tasks(self, tasks: Union[List[TaskId], List[Task]]) -> None:
        self._tasks = tasks

    @property
    def data_nodes(self) -> Dict[str, DataNode]:
        """The dictionary of data nodes used by the sequence."""
        data_nodes = {}
        list_data_nodes = [task.data_nodes for task in self._get_tasks().values()]
        for data_node in list_data_nodes:
            for k, v in data_node.items():
                data_nodes[k] = v
        return data_nodes

    @property
    def parent_ids(self) -> Set[str]:
        """The set of identifiers of the parent scenarios."""
        return self._parent_ids

    @property
    def owner_id(self) -> Optional[str]:
        """The identifier of the owner (scenario_id, cycle_id) or None."""
        return self._owner_id

    @property
    def version(self) -> str:
        """The application version of the sequence.

        The string indicates the application version of the sequence. If not
        provided, the latest version is used."""
        return self._version

    @property
    def properties(self) -> _Properties:
        """The dictionary of additional properties."""
        self._properties = _Reloader()._reload("sequence", self)._properties
        return self._properties

    @property  # type: ignore
    @_self_reload(_MANAGER_NAME)
    def subscribers(self) -> _ListAttributes:
        """The list of callbacks to be called on `Job^`'s status change."""
        return self._subscribers

    @subscribers.setter  # type: ignore
    @_self_setter(_MANAGER_NAME)
    def subscribers(self, val) -> None:
        self._subscribers = _ListAttributes(self, val)

    def get_parents(self) -> Dict[str, Set[_Entity]]:
        """Get parent scenarios of the sequence.

        Returns:
            The dictionary of all parent entities.
                They are grouped by their type (Scenario^, Sequences^, or tasks^) so each key corresponds
                to a level of the parents and the value is a set of the parent entities.
                An empty dictionary is returned if the entity does not have parents.
        """
        from ... import core as tp

        return tp.get_parents(self)

    def subscribe(
        self,
        callback: Callable[[Sequence, Job], None],
        params: Optional[List[Any]] = None,
    ) -> None:
        """Subscribe a function to be called on `Job^` status change.
        The subscription is applied to all jobs created from the sequence's execution.

        Note:
            Notification will be available only for jobs created after this subscription.

        Parameters:
            callback (Callable[[Sequence^, Job^], None]): The callable function to be called on
                status change.
            params (Optional[List[Any]]): The parameters to be passed to the _callback_.
        """
        from ... import core as tp

        return tp.subscribe_sequence(callback, params, self)

    def unsubscribe(self, callback: Callable[[Sequence, Job], None], params: Optional[List[Any]] = None) -> None:
        """Unsubscribe a function that is called when the status of a `Job^` changes.

        Note:
            The function will continue to be called for ongoing jobs.

        Parameters:
            callback (Callable[[Sequence^, Job^], None]): The callable function to unsubscribe.
            params (Optional[List[Any]]): The parameters to be passed to the _callback_.
        """
        from ... import core as tp

        return tp.unsubscribe_sequence(callback, params, self)

    def submit(
        self,
        callbacks: Optional[List[Callable]] = None,
        force: bool = False,
        wait: bool = False,
        timeout: Optional[Union[float, int]] = None,
        **properties,
    ) -> Submission:
        """Submit the sequence for execution.

        All the `Task^`s of the sequence will be submitted for execution.

        Parameters:
            callbacks (List[Callable]): The list of callable functions to be called on status
                change.
            force (bool): Force execution even if the data nodes are in cache.
            wait (bool): Wait for the orchestrated jobs created from the sequence submission to be finished
                in asynchronous mode.
            timeout (Union[float, int]): The maximum number of seconds to wait for the jobs to be finished before
                returning.<br/>
                If not provided and *wait* is True, the function waits indefinitely.
            **properties (dict[str, any]): A keyworded variable length list of additional arguments.

        Returns:
            A `Submission^` containing the information of the submission.
        """
        from ._sequence_manager_factory import _SequenceManagerFactory

        return _SequenceManagerFactory._build_manager()._submit(self, callbacks, force, wait, timeout, **properties)

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

    @staticmethod
    def _new_id(sequence_name: str, scenario_id) -> SequenceId:
        seq_id = sequence_name.replace(" ", "TPSPACE")
        return SequenceId(Sequence._SEPARATOR.join([Sequence._ID_PREFIX, _validate_id(seq_id), scenario_id]))

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


@_make_event.register(Sequence)
def _make_event_for_sequence(
    sequence: Sequence,
    operation: EventOperation,
    /,
    attribute_name: Optional[str] = None,
    attribute_value: Optional[Any] = None,
    **kwargs,
) -> Event:
    metadata = {**kwargs}
    return Event(
        entity_type=EventEntityType.SEQUENCE,
        entity_id=sequence.id,
        operation=operation,
        attribute_name=attribute_name,
        attribute_value=attribute_value,
        metadata=metadata,
    )
