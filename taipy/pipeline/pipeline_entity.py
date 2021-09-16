""" Generic pipeline.
More specific pipelines such as optimization pipeline, data preparation pipeline,
ML training pipeline, etc. should implement this generic pipeline entity
"""
import uuid
from collections import defaultdict
from typing import Dict, List

import networkx as nx

from taipy.data.data_source import DataSourceEntity
from taipy.pipeline.pipeline_model import Dag, PipelineId, PipelineModel
from taipy.task.task_entity import TaskEntity


class PipelineEntity:
    __ID_PREFIX = "PIPELINE"
    __ID_SEPARATOR = "_"

    def __init__(
        self,
        name: str,
        properties: Dict[str, str],
        task_entities: List[TaskEntity],
        pipeline_id: PipelineId = None,
    ):
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
        is_data_source = True
        for nodes in nx.topological_generations(dag):
            for node in nodes:
                if is_data_source and not isinstance(node, DataSourceEntity):
                    return False
                if not is_data_source and not isinstance(node, TaskEntity):
                    return False
            is_data_source = not is_data_source
        return True

    def __build_dag(self):
        graph = nx.DiGraph()
        for task in self.task_entities:
            for predecessor in task.input:
                graph.add_edges_from([(predecessor, task)])
            for successor in task.output:
                graph.add_edges_from([(task, successor)])
        return graph

    def to_model(self) -> PipelineModel:
        source_task_edges = defaultdict(list)
        task_source_edges = defaultdict(lambda: [])
        for task in self.task_entities:
            for predecessor in task.input:
                source_task_edges[predecessor.id].append(str(task.id))
            for successor in task.output:
                task_source_edges[str(task.id)].append(successor.id)
        return PipelineModel(
            self.id,
            self.name,
            self.properties,
            Dag(source_task_edges),
            Dag(task_source_edges),
        )

    def get_sorted_task_entities(self) -> List[List[TaskEntity]]:
        dag = self.__build_dag()
        return list(
            nodes
            for nodes in nx.topological_generations(dag)
            if (TaskEntity in (type(node) for node in nodes))
        )
