""" Generic pipeline.
More specific pipelines such as optimization pipeline, data preparation pipeline,
ML training pipeline, etc. should implement this generic pipeline entity
"""
import logging
import uuid
from collections import defaultdict
from typing import Dict, List

import networkx as nx

from taipy.data import DataSourceEntity
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
        self.name = name.strip().lower().replace(' ', '_')
        self.id: PipelineId = pipeline_id or PipelineId(
            self.__ID_SEPARATOR.join([self.__ID_PREFIX, name, str(uuid.uuid4())])
        )
        self.properties = properties
        self.task_entities = {task.name: task for task in task_entities}
        self.is_consistent = self.__is_consistent()

    def __getattr__(self, attribute_name):
        if attribute_name in self.properties:
            return self.properties[attribute_name]
        if attribute_name in self.task_entities:
            return self.task_entities[attribute_name]
        for task in self.task_entities.values():
            if attribute_name in task.input:
                return task.input[attribute_name]
            if attribute_name in task.output:
                return task.output[attribute_name]
        logging.error(f"{attribute_name} is not an attribute of pipeline {self.id}")
        raise AttributeError

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
        for task in self.task_entities.values():
            for predecessor in task.input.values():
                graph.add_edges_from([(predecessor, task)])
            for successor in task.output.values():
                graph.add_edges_from([(task, successor)])
        return graph

    def to_model(self) -> PipelineModel:
        source_task_edges = defaultdict(list)
        task_source_edges = defaultdict(lambda: [])
        for task in self.task_entities.values():
            for predecessor in task.input.values():
                source_task_edges[predecessor.id].append(str(task.id))
            for successor in task.output.values():
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
