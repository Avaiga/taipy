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

import abc
from typing import Any, Callable, List, Optional, Set, Union

import networkx as nx

from ..common._listattributes import _ListAttributes
from ..common._utils import _Subscriber
from ..data.data_node import DataNode
from ..job.job import Job
from ..task.task import Task
from ._dag import _DAG


class _Submittable:
    def __init__(self, subscribers=None):
        self._subscribers = _ListAttributes(self, subscribers or list())

    @abc.abstractmethod
    def submit(
        self,
        callbacks: Optional[List[Callable]] = None,
        force: bool = False,
        wait: bool = False,
        timeout: Optional[Union[float, int]] = None,
    ):
        raise NotImplementedError

    def _get_inputs(self) -> Set[DataNode]:
        dag = self._build_dag()
        return {node for node, degree in dict(dag.in_degree).items() if degree == 0 and isinstance(node, DataNode)}

    @abc.abstractmethod
    def subscribe(self, callback: Callable[[_Submittable, Job], None], params: Optional[List[Any]] = None):
        raise NotImplementedError

    @abc.abstractmethod
    def unsubscribe(self, callback: Callable[[_Submittable, Job], None], params: Optional[List[Any]] = None):
        raise NotImplementedError

    @abc.abstractmethod
    def _get_set_of_tasks(self) -> Set[Task]:
        raise NotImplementedError

    def _get_dag(self) -> _DAG:
        return _DAG(self._build_dag())

    def _build_dag(self) -> nx.DiGraph:
        graph = nx.DiGraph()
        tasks = self._get_set_of_tasks()
        for task in tasks:
            if has_input := task.input:
                for predecessor in task.input.values():
                    graph.add_edges_from([(predecessor, task)])
            if has_output := task.output:
                for successor in task.output.values():
                    graph.add_edges_from([(task, successor)])
            if not has_input and not has_output:
                graph.add_node(task)
        return graph

    def _get_sorted_tasks(self) -> List[List[Task]]:
        dag = self._build_dag()
        remove = [node for node, degree in dict(dag.in_degree).items() if degree == 0 and isinstance(node, DataNode)]
        dag.remove_nodes_from(remove)
        return list(nodes for nodes in nx.topological_generations(dag) if (Task in (type(node) for node in nodes)))

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
