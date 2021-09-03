""" Generic pipeline.
It just represents a descriptor of a DAG.
It is made to be overridden by more specific pipelines such as optimization pipeline, data preparation pipeline,
ML training pipeline, etc.
"""
import uuid
from taipy.pipeline.pipeline_model import PipelineModel
from taipy.pipeline.types import *
from taipy.task.task import Task
import networkx as nx
from collections import defaultdict


class Pipeline:
    ID_PREFIX = "PIPELINE"
    ID_SEPARATOR = "_"
    id: PipelineId
    name: str
    properties: dict
    tasks: list[Task]
    __is_acyclic: bool = False

    def __init__(self, pipeline_id: PipelineId, name: str, properties: dict[str, str], tasks: list[Task]):
        self.id = pipeline_id
        self.name = name
        self.properties = properties
        self.tasks = tasks
        self.__check_consistency()

    @classmethod
    def create_pipeline(cls, name: str, properties: dict[str, str], tasks: list[Task]):
        new_id = PipelineId(''.join([cls.ID_PREFIX, cls.ID_SEPARATOR, name, cls.ID_SEPARATOR, str(uuid.uuid1())]))
        pipeline = Pipeline(new_id, name, properties, tasks)
        return pipeline

    def __check_consistency(self):
        graph = nx.DiGraph()
        for task in self.tasks:
            for predecessor in task.input_data_sources:
                graph.add_edges_from([(predecessor.id, task.id)])
            for successor in task.output_data_sources:
                graph.add_edges_from([(task.id, successor.id)])
        self.__is_acyclic = nx.is_directed_acyclic_graph(graph)

    def to_model(self):
        source_task_edges: Dag = defaultdict(lambda: [])
        task_source_edges: Dag = defaultdict(lambda: [])
        for task in self.tasks:
            for predecessor in task.input_data_sources:
                source_task_edges[predecessor.id].append(task.id)
            for successor in task.output_data_sources:
                task_source_edges[task.id].append(successor.id)
        return PipelineModel(self.id, self.name, self.properties, source_task_edges, task_source_edges)
