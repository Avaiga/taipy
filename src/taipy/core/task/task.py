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

import uuid
from typing import TYPE_CHECKING, Any, Callable, Dict, Iterable, List, Optional, Set, Union

from taipy.config.common._template_handler import _TemplateHandler as _tpl
from taipy.config.common._validate_id import _validate_id
from taipy.config.common.scope import Scope

from .._entity._entity import _Entity
from .._entity._labeled import _Labeled
from .._entity._properties import _Properties
from .._entity._reload import _Reloader, _self_reload, _self_setter
from .._version._version_manager_factory import _VersionManagerFactory
from ..data._data_manager_factory import _DataManagerFactory
from ..data.data_node import DataNode
from ..exceptions.exceptions import NonExistingDataNode
from .task_id import TaskId

if TYPE_CHECKING:
    from ..job.job import Job


class Task(_Entity, _Labeled):
    """Hold a user function that will be executed, its parameters and the results.

    A `Task` brings together the user code as function, the inputs and the outputs as data nodes
    (instances of the `DataNode^` class).

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

    def __init__(
        self,
        config_id: str,
        properties: Dict[str, Any],
        function,
        input: Optional[Iterable[DataNode]] = None,
        output: Optional[Iterable[DataNode]] = None,
        id: Optional[TaskId] = None,
        owner_id: Optional[str] = None,
        parent_ids: Optional[Set[str]] = None,
        version: Optional[str] = None,
        skippable: bool = False,
    ):
        self.config_id = _validate_id(config_id)
        self.id = id or TaskId(self.__ID_SEPARATOR.join([self._ID_PREFIX, self.config_id, str(uuid.uuid4())]))
        self.owner_id = owner_id
        self._parent_ids = parent_ids or set()
        self.__input = {dn.config_id: dn for dn in input or []}
        self.__output = {dn.config_id: dn for dn in output or []}
        self._function = function
        self._version = version or _VersionManagerFactory._build_manager()._get_latest_version()
        self._skippable = skippable
        self._properties = _Properties(self, **properties)

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id

    def __getstate__(self):
        return vars(self)

    def __setstate__(self, state):
        vars(self).update(state)

    def __getattr__(self, attribute_name):
        protected_attribute_name = _validate_id(attribute_name)
        if protected_attribute_name in self._properties:
            return _tpl._replace_templates(self._properties[protected_attribute_name])
        if protected_attribute_name in self.input:
            return self.input[protected_attribute_name]
        if protected_attribute_name in self.output:
            return self.output[protected_attribute_name]
        raise AttributeError(f"{attribute_name} is not an attribute of task {self.id}")

    @property
    def properties(self):
        self._properties = _Reloader()._reload(self._MANAGER_NAME, self)._properties
        return self._properties

    def get_parents(self):
        """Get parents of the task."""
        from ... import core as tp

        return tp.get_parents(self)

    @property  # type: ignore
    @_self_reload(_MANAGER_NAME)
    def parent_ids(self):
        return self._parent_ids

    @property
    def input(self) -> Dict[str, DataNode]:
        return self.__input

    @property
    def output(self) -> Dict[str, DataNode]:
        return self.__output

    @property
    def data_nodes(self) -> Dict[str, DataNode]:
        return {**self.input, **self.output}

    @property  # type: ignore
    @_self_reload(_MANAGER_NAME)
    def function(self):
        return self._function

    @function.setter  # type: ignore
    @_self_setter(_MANAGER_NAME)
    def function(self, val):
        self._function = val

    @property  # type: ignore
    @_self_reload(_MANAGER_NAME)
    def skippable(self):
        return self._skippable

    @skippable.setter  # type: ignore
    @_self_setter(_MANAGER_NAME)
    def skippable(self, val):
        self._skippable = val

    @property
    def scope(self) -> Scope:
        """Retrieve the lowest scope of the task based on its data nodes.

        Returns:
            The lowest scope present in input and output data nodes or GLOBAL if there are
                either no input or no output.
        """
        data_nodes = list(self.__input.values()) + list(self.__output.values())
        scope = Scope(min(dn.scope for dn in data_nodes)) if len(data_nodes) != 0 else Scope.GLOBAL
        return scope

    @property
    def version(self):
        return self._version

    def submit(
        self,
        callbacks: Optional[List[Callable]] = None,
        force: bool = False,
        wait: bool = False,
        timeout: Optional[Union[float, int]] = None,
    ) -> "Job":  # noqa
        """Submit the task for execution.

        Parameters:
            callbacks (List[Callable]): The list of callable functions to be called on status
                change.
            force (bool): Force execution even if the data nodes are in cache.
            wait (bool): Wait for the orchestrated job created from the task submission to be finished in asynchronous
                mode.
            timeout (Union[float, int]): The maximum number of seconds to wait for the job to be finished before
                returning.

        Returns:
            The created `Job^`.
        """
        from ._task_manager_factory import _TaskManagerFactory

        return _TaskManagerFactory._build_manager()._submit(self, callbacks, force, wait, timeout)

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
