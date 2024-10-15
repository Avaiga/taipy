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

import abc
from typing import Any, Callable, List, Optional, Set, Union

import networkx as nx

from ..common._listattributes import _ListAttributes
from ..common._utils import _Subscriber
from ..data.data_node import DataNode
from ..job.job import Job
from ..reason import DataNodeEditInProgress, DataNodeIsNotWritten, ReasonCollection
from ..submission.submission import Submission
from ..task.task import Task
from ._dag import _DAG


class Submittable:
    """Instance of an entity that can be submitted for execution.

    A submittable holds functions that can be used to build the execution directed acyclic graph.
    """

    def __init__(self, submittable_id: str, subscribers: Optional[List[_Subscriber]] = None) -> None:
        self._submittable_id = submittable_id
        self._subscribers = _ListAttributes(self, subscribers or [])

    def get_inputs(self) -> Set[DataNode]:
        """Return the set of input data nodes of this submittable.

        Returns:
            The set of input data nodes.
        """
        dag = self._build_dag()
        return self.__get_inputs(dag)

    def get_outputs(self) -> Set[DataNode]:
        """Return the set of output data nodes of the submittable entity.

        Returns:
            The set of output data nodes.
        """
        dag = self._build_dag()
        return self.__get_outputs(dag)

    def get_intermediate(self) -> Set[DataNode]:
        """Return the set of intermediate data nodes of the submittable entity.

        Returns:
            The set of intermediate data nodes.
        """
        dag = self._build_dag()
        all_data_nodes_in_dag = {node for node in dag.nodes if isinstance(node, DataNode)}
        return all_data_nodes_in_dag - self.__get_inputs(dag) - self.__get_outputs(dag)

    def is_ready_to_run(self) -> ReasonCollection:
        """Indicate if the entity is ready to be run.

        Returns:
            A ReasonCollection object that can function as a Boolean value,
                which is True if the given entity is ready to be run or there is
                no reason to be blocked, False otherwise.
        """
        reason_collection = ReasonCollection()

        for node in self.get_inputs():
            if node._edit_in_progress:
                reason_collection._add_reason(node.id, DataNodeEditInProgress(node.id))
            if not node._last_edit_date:
                reason_collection._add_reason(node.id, DataNodeIsNotWritten(node.id))

        return reason_collection

    def data_nodes_being_edited(self) -> Set[DataNode]:
        """Return the set of data nodes that are being edited.

        Returns:
            The set of data nodes that are being edited.
        """
        dag = self._build_dag()
        return {node for node in dag.nodes if isinstance(node, DataNode) and node.edit_in_progress}

    @abc.abstractmethod
    def submit(
        self,
        callbacks: Optional[List[Callable]] = None,
        force: bool = False,
        wait: bool = False,
        timeout: Optional[Union[float, int]] = None,
    ) -> Submission:
        raise NotImplementedError

    @abc.abstractmethod
    def subscribe(self, callback: Callable[[Submittable, Job], None], params: Optional[List[Any]] = None) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def unsubscribe(self, callback: Callable[[Submittable, Job], None], params: Optional[List[Any]] = None) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def _get_set_of_tasks(self) -> Set[Task]:
        raise NotImplementedError

    @staticmethod
    def __get_inputs(dag: nx.DiGraph) -> Set[DataNode]:
        return {node for node, degree in dict(dag.in_degree).items() if degree == 0 and isinstance(node, DataNode)}

    @staticmethod
    def __get_outputs(dag: nx.DiGraph) -> set[DataNode]:
        return {node for node, degree in dict(dag.out_degree).items() if degree == 0 and isinstance(node, DataNode)}

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
        return [nodes for nodes in nx.topological_generations(dag) if (Task in (type(node) for node in nodes))]

    def _add_subscriber(self, callback: Callable, params: Optional[List[Any]] = None) -> None:
        params = [] if params is None else params
        self._subscribers.append(_Subscriber(callback=callback, params=params))

    def _remove_subscriber(self, callback: Callable, params: Optional[List[Any]] = None) -> None:
        if params is not None:
            self._subscribers.remove(_Subscriber(callback, params))
        elif elem := [x for x in self._subscribers if x.callback == callback]:
            self._subscribers.remove(elem[0])
        else:
            raise ValueError
