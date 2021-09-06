""" Generic pipeline.
It represents a descriptor of a DAG.
More specific pipelines such as optimization pipeline, data preparation pipeline,
ML training pipeline, etc. should implement this generic pipeline entity
"""
import uuid
from collections import defaultdict
from typing import Dict, List

import networkx as nx

from taipy.pipeline.pipeline_model import PipelineModel
from taipy.pipeline.types import *
from taipy.pipeline.types import Dag, PipelineId
from taipy.task.task import Task


class Pipeline:
    __ID_PREFIX = "PIPELINE"
    __ID_SEPARATOR = "_"
    id: PipelineId
    name: str
    properties: Dict
    tasks: List[Task]
    is_acyclic: bool = False

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
        self.__check_consistency()

    @classmethod
    def create_pipeline(cls, name: str, properties: Dict[str, str], tasks: List[Task]):
        new_id = PipelineId(
            "".join(
                [
                    cls.__ID_PREFIX,
                    cls.__ID_SEPARATOR,
                    name,
                    cls.__ID_SEPARATOR,
                    str(uuid.uuid4()),
                ]
            )
        )
        pipeline = Pipeline(new_id, name, properties, tasks)
        return pipeline

    def __check_consistency(self):
        graph = nx.DiGraph()
        for task in self.tasks:
            for predecessor in task.input_data_sources:
                graph.add_edges_from([(predecessor.id, task.id)])
            for successor in task.output_data_sources:
                graph.add_edges_from([(task.id, successor.id)])
        self.is_acyclic = nx.is_directed_acyclic_graph(graph)

    def to_model(self):
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
