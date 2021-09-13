""" Generic pipeline.
More specific pipelines such as optimization pipeline, data preparation pipeline,
ML training pipeline, etc. should implement this generic pipeline entity
"""
import uuid
from collections import defaultdict

import networkx as nx

from taipy.data.data_source import DataSourceEntity
from taipy.pipeline.pipeline_model import Dag, PipelineId, PipelineModel
from taipy.task.task_entity import TaskEntity
from typing import Dict, List


class PipelineEntity:
    __ID_PREFIX = "PIPELINE"
    __ID_SEPARATOR = "_"

    def __init__(self, name: str, properties: Dict[str, str], task_entities: List[TaskEntity], pipeline_id: PipelineId = None):
        self.id: PipelineId = pipeline_id or PipelineId(
                self.__ID_SEPARATOR.join([self.__ID_PREFIX, name, str(uuid.uuid4())])
        )
        self.name = name
        self.properties = properties
        self.task_entities = task_entities
        self.is_consistent = self.__is_consistent()

    def __is_consistent(self) -> bool:
        dag = self.__build_dag()
        if not nx.is_directed_acyclic_graph(dag):
            return False
        expected_type = DataSourceEntity
        for nodes in nx.topological_generations(dag):
            for node in nodes:
                if not isinstance(node, expected_type):
                    return False
            expected_type = TaskEntity if (expected_type == DataSourceEntity) else DataSourceEntity
        return True

    def __build_dag(self):
        graph = nx.DiGraph()
        for task in self.task_entities:
            for predecessor in task.input_data_sources:
                graph.add_edges_from([(predecessor, task)])
            for successor in task.output_data_sources:
                graph.add_edges_from([(task, successor)])
        return graph

    def to_model(self) -> PipelineModel:
        source_task_edges: Dag = defaultdict(lambda: [])
        task_source_edges: Dag = defaultdict(lambda: [])
        for task in self.task_entities:
            for predecessor in task.input_data_sources:
                source_task_edges[predecessor.id].append(task.id)
            for successor in task.output_data_sources:
                task_source_edges[task.id].append(successor.id)
        return PipelineModel(self.id, self.name, self.properties, source_task_edges, task_source_edges)

    def get_sorted_task_entities(self) -> List[List[TaskEntity]]:
        dag = self.__build_dag()
        return list(nodes for nodes in nx.topological_generations(dag) if (TaskEntity in (type(node) for node in nodes)))
