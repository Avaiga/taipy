""" Generic pipeline (seriously?).
More specific pipelines such as optimization pipeline, data preparation pipeline,
ML training pipeline, etc. should implement this generic pipeline entity
"""
import logging
import uuid
from typing import Callable, Dict, List, Set

from taipy.common import protect_name
from taipy.common.alias import ScenarioId
from taipy.common.utils import objs_to_dict
from taipy.cycle.cycle import Cycle
from taipy.pipeline import Pipeline
from taipy.scenario.scenario_model import ScenarioModel


class Scenario:
    __ID_PREFIX = "SCENARIO"
    __SEPARATOR = "_"

    def __init__(
        self,
        config_name: str,
        pipelines: List[Pipeline],
        properties: Dict[str, str],
        scenario_id: ScenarioId = None,
        master_scenario: bool = False,
        cycle: Cycle = None,
    ):
        self.config_name = protect_name(config_name)
        self.id: ScenarioId = scenario_id or self.new_id(self.config_name)
        self.pipelines = {p.config_name: p for p in pipelines}
        self.properties = properties
        self.master_scenario = master_scenario
        self.subscribers: Set[Callable] = set()
        self.cycle = cycle

    def __eq__(self, other):
        return self.id == other.id

    @staticmethod
    def new_id(config_name: str) -> ScenarioId:
        return ScenarioId(
            Scenario.__SEPARATOR.join([Scenario.__ID_PREFIX, protect_name(config_name), str(uuid.uuid4())])
        )

    def __getattr__(self, attribute_name):
        protected_attribute_name = protect_name(attribute_name)
        if protected_attribute_name in self.properties:
            return self.properties[protected_attribute_name]
        if protected_attribute_name in self.pipelines:
            return self.pipelines[protected_attribute_name]
        for pipeline in self.pipelines.values():
            if protected_attribute_name in pipeline.tasks:
                return pipeline.tasks[protected_attribute_name]
            for task in pipeline.tasks.values():
                if protected_attribute_name in task.input:
                    return task.input[protected_attribute_name]
                if protected_attribute_name in task.output:
                    return task.output[protected_attribute_name]
        logging.error(f"{attribute_name} is not an attribute of scenario {self.id}")
        raise AttributeError

    def add_subscriber(self, callback: Callable):
        self.subscribers.add(callback)

    def remove_subscriber(self, callback: Callable):
        self.subscribers.remove(callback)

    def to_model(self) -> ScenarioModel:
        return ScenarioModel(
            self.id,
            self.config_name,
            [pipeline.id for pipeline in self.pipelines.values()],
            self.properties,
            self.master_scenario,
            objs_to_dict(list(self.subscribers)),
            self.cycle.id if self.cycle else None,
        )

    def is_master_scenario(self) -> bool:
        return self.master_scenario
