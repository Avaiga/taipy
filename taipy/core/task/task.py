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

import uuid
from typing import Any, Callable, Dict, Iterable, List, Optional, Set, Union

from taipy.common.config.common._validate_id import _validate_id
from taipy.common.config.common.scope import Scope

from .._entity._entity import _Entity
from .._entity._labeled import _Labeled
from .._entity._properties import _Properties
from .._entity._reload import _Reloader, _self_reload, _self_setter
from .._version._version_manager_factory import _VersionManagerFactory
from ..data.data_node import DataNode
from ..exceptions import AttributeKeyAlreadyExisted
from ..notification.event import Event, EventEntityType, EventOperation, _make_event
from ..submission.submission import Submission
from .task_id import TaskId


class Task(_Entity, _Labeled):
    """Hold a user function that will be executed, its parameters and the results.

    A `Task` brings together the user code as function, the inputs and the outputs
    as data nodes (instances of the `DataNode^` class).

    !!! note
        It is not recommended to instantiate a `Task` directly. Instead, it should be
        created with the `create_scenario()^` function. When creating a `Scenario^`,
        the related data nodes and tasks are created automatically. Please refer to
        the `Scenario^` class for more information.

    A task's attributes (the input data nodes, the output data nodes, the Python
    function) are populated based on its task configuration `TaskConfig^`.

    ??? Example

        ```python
        import taipy as tp
        from taipy import Config

        def by_two(x: int):
            return x * 2

        if __name__ == "__main__":
            # Configure data nodes, tasks and scenarios
            input_cfg = Config.configure_data_node("my_input", default_data=2)
            result_cfg = Config.configure_data_node("my_result")
            task_cfg = Config.configure_task("my_double", function=by_two, input=input_cfg, output=result_cfg)
            scenario_cfg = Config.configure_scenario("my_scenario", task_configs=[task_cfg])

            # Instantiate a task along with a scenario
            sc = tp.create_scenario(scenario_cfg)

            # Retrieve task and data nodes from scenario
            task_input = sc.my_input
            double_task = sc.my_double
            task_result = sc.my_result

            # Write the input data and submit the task
            task_input.write(3)
            double_task.submit()

            # Read the result
            print(task_result.read())  # Output: 6

            # Retrieve the list of all tasks
            all_tasks = tp.get_tasks()
        ```

    Attributes:
        config_id (str): The identifier of the `TaskConfig^`.
        properties (dict[str, Any]): A dictionary of additional properties.
        function (callable): The python function to execute. The _function_ must take as parameter the
            data referenced by inputs data nodes, and must return the data referenced by outputs data nodes.
        input (Union[DataNode^, List[DataNode^]]): The list of inputs.
        output (Union[DataNode^, List[DataNode^]]): The list of outputs.
        id (str): The unique identifier of the task.
        owner_id (str):  The identifier of the owner (sequence_id, scenario_id, cycle_id) or None.
        parent_ids (Optional[Set[str]]): The set of identifiers of the parent sequences.
        version (str): The string indicates the application version of the task to instantiate. If not provided, the
            latest version is used.
        skippable (bool): If True, indicates that the task can be skipped if no change has been made on inputs. The
            default value is _False_.

    """

    _ID_PREFIX = "TASK"
    __ID_SEPARATOR = "_"
    _MANAGER_NAME = "task"
    __CHECK_INIT_DONE_ATTR_NAME = "_init_done"

    id: TaskId
    """The unique identifier of the task."""

    def __init__(
        self,
        config_id: str,
        properties: Dict[str, Any],
        function: Callable,
        input: Optional[Iterable[DataNode]] = None,
        output: Optional[Iterable[DataNode]] = None,
        id: Optional[TaskId] = None,
        owner_id: Optional[str] = None,
        parent_ids: Optional[Set[str]] = None,
        version: Optional[str] = None,
        skippable: bool = False,
    ) -> None:
        self._config_id = _validate_id(config_id)
        self.id = id or TaskId(self.__ID_SEPARATOR.join([self._ID_PREFIX, self.config_id, str(uuid.uuid4())]))
        self._owner_id = owner_id
        self._parent_ids = parent_ids or set()
        self._input = {dn.config_id: dn for dn in input or []}
        self._output = {dn.config_id: dn for dn in output or []}
        self._function = function
        self._version = version or _VersionManagerFactory._build_manager()._get_latest_version()
        self._skippable = skippable
        self._properties = _Properties(self, **properties)
        self._init_done = True

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other) -> bool:
        """Check if a task is equal to another task."""
        return isinstance(other, Task) and self.id == other.id

    def __getstate__(self):
        return vars(self)

    def __setstate__(self, state):
        vars(self).update(state)

    def __setattr__(self, name: str, value: Any) -> None:
        if self.__CHECK_INIT_DONE_ATTR_NAME not in dir(self) or name in dir(self):
            return super().__setattr__(name, value)
        else:
            try:
                self.__getattr__(name)
                raise AttributeKeyAlreadyExisted(name)
            except AttributeError:
                return super().__setattr__(name, value)

    def __getattr__(self, attribute_name) -> Any:
        protected_attribute_name = _validate_id(attribute_name)
        if protected_attribute_name in self.input:
            return self.input[protected_attribute_name]
        if protected_attribute_name in self.output:
            return self.output[protected_attribute_name]
        raise AttributeError(f"{attribute_name} is not an attribute of task {self.id}")

    @property
    def properties(self) -> _Properties:
        """Dictionary of additional properties."""
        self._properties = _Reloader()._reload(self._MANAGER_NAME, self)._properties
        return self._properties

    @property
    def config_id(self) -> str:
        """The identifier of the `TaskConfig^`."""
        return self._config_id

    @property
    def owner_id(self) -> Optional[str]:
        """The identifier of the owner (scenario_id or cycle_id) or None."""
        return self._owner_id

    @property  # type: ignore
    @_self_reload(_MANAGER_NAME)
    def parent_ids(self) -> Set[str]:
        """The set of identifiers of the parent scenarios."""
        return self._parent_ids

    @property
    def input(self) -> Dict[str, DataNode]:
        """The dictionary of input data nodes."""
        return self._input

    @property
    def output(self) -> Dict[str, DataNode]:
        """The dictionary of output data nodes."""
        return self._output

    @property
    def data_nodes(self) -> Dict[str, DataNode]:
        """The dictionary of input and output data nodes."""
        return {**self.input, **self.output}

    @property  # type: ignore
    @_self_reload(_MANAGER_NAME)
    def function(self) -> Callable:
        """The python function to execute."""
        return self._function

    @function.setter  # type: ignore
    @_self_setter(_MANAGER_NAME)
    def function(self, val) -> None:
        self._function = val

    @property  # type: ignore
    @_self_reload(_MANAGER_NAME)
    def skippable(self) -> bool:
        """True if the task can be skipped if no change has been made on inputs. False otherwise"""
        return self._skippable

    @skippable.setter  # type: ignore
    @_self_setter(_MANAGER_NAME)
    def skippable(self, val) -> None:
        self._skippable = val

    @property
    def scope(self) -> Scope:
        """The lowest scope of the task's data nodes.

        The lowest scope present in input and output data nodes or GLOBAL if there are
        either no input or no output.
        """
        data_nodes = list(self._input.values()) + list(self._output.values())
        return Scope(min(dn.scope for dn in data_nodes)) if len(data_nodes) != 0 else Scope.GLOBAL

    @property
    def version(self) -> str:
        """The application version of the task.

        The string indicates the application version of the task. If not
        provided, the latest version is used."""
        return self._version

    def submit(
        self,
        callbacks: Optional[List[Callable]] = None,
        force: bool = False,
        wait: bool = False,
        timeout: Optional[Union[float, int]] = None,
        **properties,
    ) -> Submission:
        """Submit the task for execution.

        Parameters:
            callbacks (List[Callable]): The list of callable functions to be called on status
                change.
            force (bool): Force execution even if the data nodes are in cache.
            wait (bool): Wait for the orchestrated job created from the task submission to be finished in asynchronous
                mode.
            timeout (Union[float, int]): The maximum number of seconds to wait for the job to be finished before
                returning.<br/>
                If not provided and *wait* is True, the function waits indefinitely.
            **properties (dict[str, any]): A keyworded variable length list of additional arguments.

        Returns:
            A `Submission^` containing the information of the submission.
        """
        from ._task_manager_factory import _TaskManagerFactory

        return _TaskManagerFactory._build_manager()._submit(self, callbacks, force, wait, timeout, **properties)

    def get_parents(self) -> Dict[str, Set[_Entity]]:
        """Get the parent scenarios of the task.

        Returns:
            The dictionary of all parent entities.
                They are grouped by their type (Scenario^, Sequences^, or tasks^) so each key corresponds
                to a level of the parents and the value is a set of the parent entities.
                An empty dictionary is returned if the entity does not have parents.
        """
        from ... import core as tp

        return tp.get_parents(self)

    def get_label(self) -> str:
        """Returns the task simple label prefixed by its owner label.

        Returns:
            The label of the task as a string.
        """
        return self._get_label()

    def get_simple_label(self) -> str:
        """Returns the task simple label.

        Returns:
            The simple label of the task as a string.
        """
        return self._get_simple_label()


@_make_event.register(Task)
def _make_event_for_task(
    task: Task,
    operation: EventOperation,
    /,
    attribute_name: Optional[str] = None,
    attribute_value: Optional[Any] = None,
    **kwargs,
) -> Event:
    metadata = {"version": task.version, "config_id": task.config_id, **kwargs}
    return Event(
        entity_type=EventEntityType.TASK,
        entity_id=task.id,
        operation=operation,
        attribute_name=attribute_name,
        attribute_value=attribute_value,
        metadata=metadata,
    )
