""" Generic pipeline.
It represents a descriptor of a DAG.
More specific pipelines such as optimization pipeline, data preparation pipeline,
ML training pipeline, etc. should implement this generic pipeline entity
"""
import uuid
from collections import defaultdict
from typing import Any, Dict, List

import networkx as nx

from taipy.data.data_source import DataSourceEntity
from taipy.pipeline.pipeline_model import Dag, PipelineId, PipelineModel
from taipy.task.task import Task


class Pipeline:
    __ID_PREFIX = "PIPELINE"
    __ID_SEPARATOR = "_"

    def __init__(
        self,
        pipeline_id: PipelineId,
        name: str,
        properties: Dict[str, str],
        tasks: List[Task],
    ):
        self.id = pipeline_id
        self.name = name
        self.properties = properties
        self.tasks = tasks
        self.is_consistent = self.__is_consistent()

    @classmethod
    def create_pipeline(cls, name: str, properties: Dict[str, str], tasks: List[Task]):
        new_id = PipelineId(
            cls.__ID_SEPARATOR.join([cls.__ID_PREFIX, name, str(uuid.uuid4())])
        )
        pipeline = Pipeline(new_id, name, properties, tasks)
        return pipeline

    def __is_consistent(self) -> bool:
        dag = self.__build_dag()
        if not nx.is_directed_acyclic_graph(dag):
            return False
        expected_type: Any = DataSourceEntity
        for nodes in nx.topological_generations(dag):
            for node in nodes:
                if not isinstance(node, expected_type):
                    return False
            expected_type = (
                Task if (expected_type == DataSourceEntity) else DataSourceEntity
            )
        return True

    def __build_dag(self):
        graph = nx.DiGraph()
        for task in self.tasks:
            for predecessor in task.input_data_sources:
                graph.add_edges_from([(predecessor, task)])
            for successor in task.output_data_sources:
                graph.add_edges_from([(task, successor)])
        return graph

    def to_model(self) -> PipelineModel:
        source_task_edges: Dag = defaultdict(lambda: [])
        task_source_edges: Dag = defaultdict(lambda: [])
        for task in self.tasks:
            for predecessor in task.input_data_sources:
                source_task_edges[predecessor.id].append(task.id)
            for successor in task.output_data_sources:
                task_source_edges[task.id].append(successor.id)
        return PipelineModel(
            self.id, self.name, self.properties, source_task_edges, task_source_edges
        )

    def get_sorted_tasks(self) -> List[List[Task]]:
        dag = self.__build_dag()
        return list(
            nodes
            for nodes in nx.topological_generations(dag)
            if (Task in (type(node) for node in nodes))
        )
