import logging
import uuid
from datetime import datetime
from typing import Callable, Dict, List, Set

from taipy.common import protect_name
from taipy.common.alias import ScenarioId
from taipy.common.utils import fcts_to_dict
from taipy.cycle.cycle import Cycle
from taipy.pipeline import Pipeline
from taipy.scenario.scenario_model import ScenarioModel


class Scenario:
    """
    Represents an instance of the  business case to solve.

    It holds a set of pipelines to submit for execution in order to solve the business case.

    Attributes:
        config_name (str):  Name that identifies the scenario configuration.
            We strongly recommend to use lowercase alphanumeric characters, dash characters ('-'),
            or underscore characters ('_').
            Other characters are replaced according the following rules:
            - Space characters are replaced by underscore characters ('_').
            - Unicode characters are replaced by a corresponding alphanumeric character using the Unicode library.
            - Other characters are replaced by dash characters ('-').
        pipelines (List[Pipeline]): List of pipelines.
        properties (dict): Dictionary of additional properties of the scenario.
        scenario_id (str): Unique identifier of this scenario. Will be generated if None value provided.
        creation_date (datetime): Date and time of the creation of the scenario.
        is_master (bool): True if the scenario is the master of its cycle. False otherwise.
        cycle (Cycle): Cycle of the scenario.
    """

    __ID_PREFIX = "SCENARIO"
    __SEPARATOR = "_"

    def __init__(
        self,
        config_name: str,
        pipelines: List[Pipeline],
        properties: Dict[str, str],
        scenario_id: ScenarioId = None,
        creation_date=None,
        is_master: bool = False,
        cycle: Cycle = None,
    ):
        self.config_name = protect_name(config_name)
        self.id: ScenarioId = scenario_id or self.new_id(self.config_name)
        self.pipelines = {p.config_name: p for p in pipelines}
        self.properties = properties
        self.creation_date = creation_date or datetime.now()
        self.master_scenario = is_master
        self.subscribers: Set[Callable] = set()
        self.cycle = cycle

    def __eq__(self, other):
        return self.id == other.id

    @staticmethod
    def new_id(config_name: str) -> ScenarioId:
        """Generates a unique scenario identifier."""
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
        """Adds callback function to be called when executing the scenario each time a scenario job changes status"""
        self.subscribers.add(callback)

    def remove_subscriber(self, callback: Callable):
        """Removes callback function"""
        self.subscribers.remove(callback)

    def to_model(self) -> ScenarioModel:
        return ScenarioModel(
            self.id,
            self.config_name,
            [pipeline.id for pipeline in self.pipelines.values()],
            self.properties,
            self.creation_date.isoformat(),
            self.master_scenario,
            fcts_to_dict(list(self.subscribers)),
            self.cycle.id if self.cycle else None,
        )
