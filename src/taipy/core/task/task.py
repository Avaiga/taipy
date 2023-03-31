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
from typing import Any, Callable, Dict, Iterable, List, Optional, Set, Union

from taipy.config.common._template_handler import _TemplateHandler as _tpl
from taipy.config.common._validate_id import _validate_id
from taipy.config.common.scope import Scope

from .._version._utils import _migrate_entity
from .._version._version_manager_factory import _VersionManagerFactory
from ..common._entity import _Entity
from ..common._properties import _Properties
from ..common._reload import _Reloader, _self_reload, _self_setter
from ..common._utils import _load_fct
from ..common._warnings import _warn_deprecated
from ..common.alias import TaskId
from ..data._data_manager_factory import _DataManagerFactory
from ..data.data_node import DataNode
from ..exceptions.exceptions import NonExistingDataNode
from ._task_model import _TaskModel


class Task(_Entity):
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
        owner_id (str):  The identifier of the owner (pipeline_id, scenario_id, cycle_id) or None.
        parent_ids (Optional[Set[str]]): The set of identifiers of the parent pipelines.
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

    @property  # type: ignore
    @_self_reload(_MANAGER_NAME)
    def skippable(self):
        return self._skippable

    @skippable.setter  # type: ignore
    @_self_setter(_MANAGER_NAME)
    def skippable(self, val):
        self._skippable = val

    @property
    def properties(self):
        self._properties = _Reloader()._reload(self._MANAGER_NAME, self)._properties
        return self._properties

    @property
    def parent_id(self):
        """Deprecated. Use owner_id instead."""
        _warn_deprecated("parent_id", suggest="owner_id")
        return self.owner_id

    @parent_id.setter
    def parent_id(self, val):
        """Deprecated. Use owner_id instead."""
        _warn_deprecated("parent_id", suggest="owner_id")
        self.owner_id = val

    def get_parents(self):
        """Get parents of the task."""
        from ... import core as tp

        return tp.get_parents(self)

    @property  # type: ignore
    @_self_reload(_MANAGER_NAME)
    def parent_ids(self):
        return self._parent_ids

    def __hash__(self):
        return hash(self.id)

    def __getstate__(self):
        return vars(self)

    def __setstate__(self, state):
        vars(self).update(state)

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
    def scope(self) -> Scope:
        """Retrieve the lowest scope of the task based on its data nodes.

        Returns:
            The lowest scope present in input and output data nodes or GLOBAL if there are
                either no input or no output.
        """
        data_nodes = list(self.__input.values()) + list(self.__output.values())
        scope = min(dn.scope for dn in data_nodes) if len(data_nodes) != 0 else Scope.GLOBAL
        return Scope(scope)

    @property
    def version(self):
        return self._version

    @version.setter
    def version(self, val):
        self._version = val

    def submit(
        self,
        callbacks: Optional[List[Callable]] = None,
        force: bool = False,
        wait: bool = False,
        timeout: Optional[Union[float, int]] = None,
    ):
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

        _TaskManagerFactory._build_manager()._submit(self, callbacks, force, wait, timeout)

    @classmethod
    def _to_model(cls, task) -> _TaskModel:
        return _TaskModel(
            id=task.id,
            owner_id=task.owner_id,
            parent_ids=list(task._parent_ids),
            config_id=task.config_id,
            input_ids=cls.__to_ids(task.input.values()),
            function_name=task._function.__name__,
            function_module=task._function.__module__,
            output_ids=cls.__to_ids(task.output.values()),
            version=task.version,
            skippable=task._skippable,
            properties=task._properties.data.copy(),
        )

    @classmethod
    def _from_model(cls, model: _TaskModel):
        task = Task(
            id=TaskId(model.id),
            owner_id=model.owner_id,
            parent_ids=set(model.parent_ids),
            config_id=model.config_id,
            function=_load_fct(model.function_module, model.function_name),
            input=cls.__to_data_nodes(model.input_ids),
            output=cls.__to_data_nodes(model.output_ids),
            version=model.version,
            skippable=model.skippable,
            properties=model.properties,
        )
        return _migrate_entity(task)

    @staticmethod
    def __to_ids(data_nodes):
        return [i.id for i in data_nodes]

    @staticmethod
    def __to_data_nodes(data_nodes_ids):
        data_nodes = []
        data_manager = _DataManagerFactory._build_manager()
        for _id in data_nodes_ids:
            if data_node := data_manager._get(_id):
                data_nodes.append(data_node)
            else:
                raise NonExistingDataNode(_id)
        return data_nodes
