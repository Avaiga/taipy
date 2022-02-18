import uuid
from collections import defaultdict
from typing import Callable, Dict, List, Optional, Set

import networkx as nx

from taipy.core.common.alias import Dag, PipelineId
from taipy.core.common.reload import reload, self_reload
from taipy.core.common.unicode_to_python_variable_name import protect_name
from taipy.core.common.utils import fcts_to_dict
from taipy.core.common.wrapper import Properties
from taipy.core.data.data_node import DataNode
from taipy.core.pipeline.pipeline_model import PipelineModel
from taipy.core.task.task import Task


class Pipeline:
    """
    A Pipeline entity that holds a list of tasks and additional arguments representing a set of data processing elements
    connected in series.

    Attributes:
        config_name (str):  Name that identifies the pipeline configuration.
            We strongly recommend to use lowercase alphanumeric characters, dash characters ('-'),
            or underscore characters ('_').
            Other characters are replaced according the following rules:
            - Space characters are replaced by underscore characters ('_').
            - Unicode characters are replaced by a corresponding alphanumeric character using the Unicode library.
            - Other characters are replaced by dash characters ('-').
        properties (dict):  List of additional arguments.
        tasks (List[Task]): List of tasks.
        pipeline_id (str): Unique identifier of this pipeline.
        parent_id (str):  Identifier of the parent (pipeline_id, scenario_id, cycle_id) or `None`.
    """

    ID_PREFIX = "PIPELINE"
    __SEPARATOR = "_"

    def __init__(
        self,
        config_name: str,
        properties: Dict[str, str],
        tasks: List[Task],
        pipeline_id: PipelineId = None,
        parent_id: Optional[str] = None,
        subscribers: Set[Callable] = None,
    ):
        self.config_name = protect_name(config_name)
        self.tasks = {task.config_name: task for task in tasks}
        self.id: PipelineId = pipeline_id or self.new_id(self.config_name)
        self.parent_id = parent_id
        self.is_consistent = self.__is_consistent()

        self._subscribers = subscribers or set()
        self._properties = Properties(self, **properties)

    def __getstate__(self):
        return self.id

    def __setstate__(self, id):
        from taipy.core.pipeline.pipeline_manager import PipelineManager

        p = PipelineManager.get(id)
        self.__dict__ = p.__dict__

    @property  # type: ignore
    @self_reload("pipeline")
    def subscribers(self):
        return self._subscribers

    @property  # type: ignore
    def properties(self):
        self._properties = reload("pipeline", self)._properties
        return self._properties

    def __eq__(self, other):
        return self.id == other.id

    @staticmethod
    def new_id(config_name: str) -> PipelineId:
        return PipelineId(Pipeline.__SEPARATOR.join([Pipeline.ID_PREFIX, protect_name(config_name), str(uuid.uuid4())]))

    def __getattr__(self, attribute_name):
        protected_attribute_name = protect_name(attribute_name)
        if protected_attribute_name in self.properties:
            return self.properties[protected_attribute_name]
        if protected_attribute_name in self.tasks:
            return self.tasks[protected_attribute_name]
        for task in self.tasks.values():
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
        for task in self.tasks.values():
            for predecessor in task.input.values():
                graph.add_edges_from([(predecessor, task)])
            for successor in task.output.values():
                graph.add_edges_from([(task, successor)])
        return graph

    def add_subscriber(self, callback: Callable):
        self._subscribers = reload("pipeline", self)._subscribers
        self._subscribers.add(callback)

    def remove_subscriber(self, callback: Callable):
        self._subscribers = reload("pipeline", self)._subscribers
        self._subscribers.remove(callback)

    def to_model(self) -> PipelineModel:
        datanode_task_edges = defaultdict(list)
        task_datanode_edges = defaultdict(list)
        for task in self.tasks.values():
            for predecessor in task.input.values():
                datanode_task_edges[str(predecessor.id)].append(str(task.id))
            for successor in task.output.values():
                task_datanode_edges[str(task.id)].append(str(successor.id))
        return PipelineModel(
            self.id,
            self.parent_id,
            self.config_name,
            self._properties.data,
            Dag(dict(datanode_task_edges)),
            Dag(dict(task_datanode_edges)),
            fcts_to_dict(list(self._subscribers)),
        )

    def get_sorted_tasks(self) -> List[List[Task]]:
        dag = self.__build_dag()
        return list(nodes for nodes in nx.topological_generations(dag) if (Task in (type(node) for node in nodes)))
