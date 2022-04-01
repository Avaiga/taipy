from __future__ import annotations

import uuid
from typing import Any, Callable, Dict, List, Optional

import networkx as nx

from taipy.core.common._entity import _Entity
from taipy.core.common._listattributes import _ListAttributes
from taipy.core.common._properties import _Properties
from taipy.core.common._reload import _reload, _self_reload, _self_setter
from taipy.core.common._validate_id import _validate_id
from taipy.core.common.alias import PipelineId
from taipy.core.data.data_node import DataNode
from taipy.core.job.job import Job
from taipy.core.task.task import Task


class Pipeline(_Entity):
    """List of `Task^`s and additional attributes representing a set of data processing
    elements connected as a direct acyclic graph.

    Attributes:
        config_id (str): The identifier of the `PipelineConfig^`.
        properties (dict[str, Any]): A dictionary of additional properties.
        tasks (List[Task^]): The list of `Task`s.
        pipeline_id (str): The Unique identifier of the pipeline.
        parent_id (str):  The identifier of the parent (scenario_id, cycle_id) or None.
    """

    _ID_PREFIX = "PIPELINE"
    __SEPARATOR = "_"
    _MANAGER_NAME = "pipeline"

    def __init__(
        self,
        config_id: str,
        properties: Dict[str, Any],
        tasks: List[Task],
        pipeline_id: PipelineId = None,
        parent_id: Optional[str] = None,
        subscribers: List[Callable] = None,
    ):
        self.config_id = _validate_id(config_id)
        self.id: PipelineId = pipeline_id or self._new_id(self.config_id)
        self.parent_id = parent_id
        self._tasks = {task.config_id: task for task in tasks}
        self.is_consistent = self.__is_consistent()

        self._subscribers = _ListAttributes(self, subscribers or list())
        self._properties = _Properties(self, **properties)

    def __getstate__(self):
        return self.id

    def __setstate__(self, id):
        from taipy.core.pipeline._pipeline_manager import _PipelineManager

        p = _PipelineManager._get(id)
        self.__dict__ = p.__dict__

    @property  # type: ignore
    @_self_reload(_MANAGER_NAME)
    def tasks(self):
        return self._tasks

    @tasks.setter  # type: ignore
    @_self_setter(_MANAGER_NAME)
    def tasks(self, val):
        self._tasks = {task.config_id: task for task in val}

    @property  # type: ignore
    @_self_reload(_MANAGER_NAME)
    def subscribers(self):
        return self._subscribers

    @subscribers.setter  # type: ignore
    @_self_setter(_MANAGER_NAME)
    def subscribers(self, val):
        self._subscribers = val or set()

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
        if protected_attribute_name in self.properties:
            return self.properties[protected_attribute_name]
        if protected_attribute_name in self._tasks:
            return self._tasks[protected_attribute_name]
        for task in self._tasks.values():
            if protected_attribute_name in task.input:
                return task.input[protected_attribute_name]
            if protected_attribute_name in task.output:
                return task.output[protected_attribute_name]
        raise AttributeError(f"{attribute_name} is not an attribute of pipeline {self.id}")

    def __is_consistent(self) -> bool:
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
        for task in self._tasks.values():
            if has_input := task.input:
                for predecessor in task.input.values():
                    graph.add_edges_from([(predecessor, task)])
            if has_output := task.output:
                for successor in task.output.values():
                    graph.add_edges_from([(task, successor)])
            if not has_input and not has_output:
                graph.add_node(task)
        return graph

    @property  # type: ignore
    @_self_reload(_MANAGER_NAME)
    def subscribers(self):
        return self._subscribers

    @subscribers.setter  # type: ignore
    @_self_setter(_MANAGER_NAME)
    def subscribers(self, val):
        self._subscribers = _ListAttributes(self, val)

    def _add_subscriber(self, callback: Callable):
        self._subscribers.append(callback)

    def _remove_subscriber(self, callback: Callable):
        self._subscribers.remove(callback)

    def _get_sorted_tasks(self) -> List[List[Task]]:
        dag = self.__build_dag()
        return list(nodes for nodes in nx.topological_generations(dag) if (Task in (type(node) for node in nodes)))

    def subscribe(self, callback: Callable[[Pipeline, Job], None]):
        """Subscribe a function to be called on `Job^` status change.
        
        The subscription is applied to all jobs created from the pipeline's execution.

        Parameters:
            callback (Callable[[Pipeline^, Job^], None]): The callable function to be called on
                status change.
        Note:
            Notification will be available only for jobs created after this subscription.
        """
        from taipy.core.pipeline._pipeline_manager import _PipelineManager

        return _PipelineManager._subscribe(callback, self)

    def unsubscribe(self, callback: Callable[[Pipeline, Job], None]):
        """Unsubscribe a function that is called when the status of a `Job^` changes.

        Parameters:
            callback (Callable[[Pipeline^, Job^], None]): The callable function to unsubscribe.
        Note:
            The function will continue to be called for ongoing jobs.
        """
        from taipy.core.pipeline._pipeline_manager import _PipelineManager

        return _PipelineManager._unsubscribe(callback, self)

    def submit(self, callbacks: Optional[List[Callable]] = None, force: bool = False):
        """Submit the pipeline for execution.

        All the `Task^`s of the pipeline will be submitted for execution.

        Parameters:
            callbacks (List[Callable]): The list of callable functions to be called on status
                change.
            force (bool): Force execution even if the data nodes are in cache.
        """
        from taipy.core.pipeline._pipeline_manager import _PipelineManager

        return _PipelineManager._submit(self, callbacks, force)
