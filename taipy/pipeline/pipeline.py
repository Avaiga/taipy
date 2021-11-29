"""Generic pipeline.

More specific pipelines such as optimization pipeline, data preparation pipeline,
Machine-Learning training pipeline, etc. could implement this generic pipeline.
"""
import logging
import uuid
from collections import defaultdict
from typing import Callable, Dict, List, Optional, Set

import networkx as nx

from taipy.common import protect_name
from taipy.common.alias import Dag, PipelineId
from taipy.common.utils import fcts_to_dict
from taipy.data import DataSource
from taipy.pipeline.pipeline_model import PipelineModel
from taipy.task.task import Task


class Pipeline:
    __ID_PREFIX = "PIPELINE"
    __SEPARATOR = "_"

    def __init__(
        self,
        config_name: str,
        properties: Dict[str, str],
        tasks: List[Task],
        pipeline_id: PipelineId = None,
        parent_id: Optional[str] = None,
    ):
        self.config_name = protect_name(config_name)
        self.properties = properties
        self.tasks = {task.config_name: task for task in tasks}
        self.id: PipelineId = pipeline_id or self.new_id(self.config_name)
        self.parent_id = parent_id
        self.is_consistent = self.__is_consistent()
        self.subscribers: Set[Callable] = set()

    def __eq__(self, other):
        return self.id == other.id

    @staticmethod
    def new_id(config_name: str) -> PipelineId:
        return PipelineId(
            Pipeline.__SEPARATOR.join([Pipeline.__ID_PREFIX, protect_name(config_name), str(uuid.uuid4())])
        )

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
        logging.error(f"{attribute_name} is not an attribute of pipeline {self.id}")
        raise AttributeError

    def __is_consistent(self) -> bool:
        dag = self.__build_dag()
        if not nx.is_directed_acyclic_graph(dag):
            return False
        is_data_source = True
        for nodes in nx.topological_generations(dag):
            for node in nodes:
                if is_data_source and not isinstance(node, DataSource):
                    return False
                if not is_data_source and not isinstance(node, Task):
                    return False
            is_data_source = not is_data_source
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
        self.subscribers.add(callback)

    def remove_subscriber(self, callback: Callable):
        self.subscribers.remove(callback)

    def to_model(self) -> PipelineModel:
        source_task_edges = defaultdict(list)
        task_source_edges = defaultdict(list)
        for task in self.tasks.values():
            for predecessor in task.input.values():
                source_task_edges[str(predecessor.id)].append(str(task.id))
            for successor in task.output.values():
                task_source_edges[str(task.id)].append(str(successor.id))
        return PipelineModel(
            self.id,
            self.parent_id,
            self.config_name,
            self.properties,
            Dag(dict(source_task_edges)),
            Dag(dict(task_source_edges)),
            fcts_to_dict(list(self.subscribers)),
        )

    def get_sorted_tasks(self) -> List[List[Task]]:
        dag = self.__build_dag()
        return list(nodes for nodes in nx.topological_generations(dag) if (Task in (type(node) for node in nodes)))
