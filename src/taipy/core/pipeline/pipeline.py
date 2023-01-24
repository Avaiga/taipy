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

import uuid
from typing import Any, Callable, Dict, List, Optional, Set, Union

import networkx as nx

from taipy.config.common._template_handler import _TemplateHandler as _tpl
from taipy.config.common._validate_id import _validate_id

from .._version._version_manager_factory import _VersionManagerFactory
from ..common._entity import _Entity
from ..common._listattributes import _ListAttributes
from ..common._properties import _Properties
from ..common._reload import _reload, _self_reload, _self_setter
from ..common._utils import _Subscriber
from ..common._warnings import _warn_deprecated
from ..common.alias import PipelineId, TaskId
from ..data.data_node import DataNode
from ..exceptions.exceptions import NonExistingTask
from ..job.job import Job
from ..task.task import Task


class Pipeline(_Entity):
    """List of `Task^`s and additional attributes representing a set of data processing
    elements connected as a direct acyclic graph.

    Attributes:
        config_id (str): The identifier of the `PipelineConfig^`.
        properties (dict[str, Any]): A dictionary of additional properties.
        tasks (List[Task^]): The list of `Task`s.
        pipeline_id (str): The Unique identifier of the pipeline.
        owner_id (str):  The identifier of the owner (scenario_id, cycle_id) or None.
        parent_ids (Optional[Set[str]]): The set of identifiers of the parent scenarios.
        version (str): The string indicates the application version of the pipeline to instantiate. If not provided,
            the latest version is used.
    """

    _ID_PREFIX = "PIPELINE"
    __SEPARATOR = "_"
    _MANAGER_NAME = "pipeline"

    def __init__(
        self,
        config_id: str,
        properties: Dict[str, Any],
        tasks: Union[List[TaskId], List[Task], List[Union[TaskId, Task]]],
        pipeline_id: PipelineId = None,
        owner_id: Optional[str] = None,
        parent_ids: Optional[Set[str]] = None,
        subscribers: List[_Subscriber] = None,
        version: str = None,
    ):
        self.config_id = _validate_id(config_id)
        self.id: PipelineId = pipeline_id or self._new_id(self.config_id)
        self.owner_id = owner_id
        self._parent_ids = parent_ids or set()
        self._tasks = tasks

        self._subscribers = _ListAttributes(self, subscribers or list())
        self._properties = _Properties(self, **properties)

        self._version = version or _VersionManagerFactory._build_manager()._get_latest_version()

    @property  # type: ignore
    def parent_id(self):
        """
        Deprecated. Use owner_id instead.
        """
        _warn_deprecated("parent_id", suggest="owner_id")
        return self.owner_id

    @parent_id.setter  # type: ignore
    def parent_id(self, val):
        """
        Deprecated. Use owner_id instead.
        """
        _warn_deprecated("parent_id", suggest="owner_id")
        self.owner_id = val

    @property  # type: ignore
    @_self_reload(_MANAGER_NAME)
    def parent_ids(self):
        return self._parent_ids

    def __getstate__(self):
        return self.id

    def __setstate__(self, id):
        import taipy.core as tp

        p = tp.get(id)
        self.__dict__ = p.__dict__

    def __hash__(self):
        return hash(self.id)

    @property  # type: ignore
    @_self_reload(_MANAGER_NAME)
    def tasks(self):
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

    @property  # type: ignore
    @_self_reload(_MANAGER_NAME)
    def subscribers(self):
        return self._subscribers

    @subscribers.setter  # type: ignore
    @_self_setter(_MANAGER_NAME)
    def subscribers(self, val):
        self._subscribers = val or set()

    @property  # type: ignore
    def version(self):
        return self._version

    @property  # type: ignore
    def properties(self):
        self._properties = _reload("pipeline", self)._properties
        return self._properties

    def __eq__(self, other):
        return self.id == other.id

    @staticmethod
    def _new_id(config_id: str) -> PipelineId:
        return PipelineId(Pipeline.__SEPARATOR.join([Pipeline._ID_PREFIX, _validate_id(config_id), str(uuid.uuid4())]))

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
        raise AttributeError(f"{attribute_name} is not an attribute of pipeline {self.id}")

    def _is_consistent(self) -> bool:
        dag = self.__build_dag()
        if not nx.is_directed_acyclic_graph(dag):
            return False
        is_data_node = True
        for nodes in nx.topological_generations(dag):
            for node in nodes:
                if is_data_node and not isinstance(node, DataNode):
                    return False
                if not is_data_node and not isinstance(node, Task):
                    return False
            is_data_node = not is_data_node
        return True

    def __build_dag(self):
        graph = nx.DiGraph()
        tasks = self._get_tasks()
        for task in tasks.values():
            if has_input := task.input:
                for predecessor in task.input.values():
                    graph.add_edges_from([(predecessor, task)])
            if has_output := task.output:
                for successor in task.output.values():
                    graph.add_edges_from([(task, successor)])
            if not has_input and not has_output:
                graph.add_node(task)
        return graph

    def _get_tasks(self):
        from ..task._task_manager_factory import _TaskManagerFactory

        tasks = {}
        task_manager = _TaskManagerFactory._build_manager()
        for task_or_id in self._tasks:
            t = task_manager._get(task_or_id, task_or_id)
            if not isinstance(t, Task):
                raise NonExistingTask(task_or_id)
            tasks[t.config_id] = t

        return tasks

    @property  # type: ignore
    @_self_reload(_MANAGER_NAME)
    def subscribers(self):
        return self._subscribers

    @subscribers.setter  # type: ignore
    @_self_setter(_MANAGER_NAME)
    def subscribers(self, val):
        self._subscribers = _ListAttributes(self, val)

    def _add_subscriber(self, callback: Callable, params: Optional[List[Any]] = None):
        params = [] if params is None else params
        self._subscribers.append(_Subscriber(callback=callback, params=params))

    def _remove_subscriber(self, callback: Callable, params: Optional[List[Any]] = None):
        if params is not None:
            self._subscribers.remove(_Subscriber(callback, params))
        else:
            elem = [x for x in self._subscribers if x.callback == callback]
            if not elem:
                raise ValueError
            self._subscribers.remove(elem[0])

    def _get_sorted_tasks(self) -> List[List[Task]]:
        dag = self.__build_dag()
        remove = [node for node, degree in dict(dag.in_degree).items() if degree == 0 and isinstance(node, DataNode)]
        dag.remove_nodes_from(remove)
        return list(nodes for nodes in nx.topological_generations(dag) if (Task in (type(node) for node in nodes)))

    def get_parents(self):
        """Get parents of the pipeline entity"""
        from ... import core as tp

        return tp.get_parents(self)

    def subscribe(
        self,
        callback: Callable[[Pipeline, Job], None],
        params: Optional[List[Any]] = None,
    ):
        """Subscribe a function to be called on `Job^` status change.
        The subscription is applied to all jobs created from the pipeline's execution.

        Parameters:
            callback (Callable[[Pipeline^, Job^], None]): The callable function to be called on
                status change.
            params (Optional[List[Any]]): The parameters to be passed to the _callback_.
        Note:
            Notification will be available only for jobs created after this subscription.
        """
        from ... import core as tp

        return tp.subscribe_pipeline(callback, params, self)

    def unsubscribe(self, callback: Callable[[Pipeline, Job], None], params: Optional[List[Any]] = None):
        """Unsubscribe a function that is called when the status of a `Job^` changes.

        Parameters:
            callback (Callable[[Pipeline^, Job^], None]): The callable function to unsubscribe.
            params (Optional[List[Any]]): The parameters to be passed to the _callback_.
        Note:
            The function will continue to be called for ongoing jobs.
        """
        from ... import core as tp

        return tp.unsubscribe_pipeline(callback, params, self)

    def submit(
        self,
        callbacks: Optional[List[Callable]] = None,
        force: bool = False,
        wait: bool = False,
        timeout: Optional[Union[float, int]] = None,
    ):
        """Submit the pipeline for execution.

        All the `Task^`s of the pipeline will be submitted for execution.

        Parameters:
            callbacks (List[Callable]): The list of callable functions to be called on status
                change.
            force (bool): Force execution even if the data nodes are in cache.
            wait (bool): Wait for the scheduled jobs created from the pipeline submission to be finished in asynchronous
                mode.
            timeout (Union[float, int]): The maximum number of seconds to wait for the jobs to be finished before
                returning.

        """
        from ._pipeline_manager_factory import _PipelineManagerFactory

        return _PipelineManagerFactory._build_manager()._submit(self, callbacks, force, wait, timeout)
