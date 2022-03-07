import uuid
from datetime import datetime
from typing import Any, Callable, Dict, List, Set

from taipy.core.common._properties import _Properties
from taipy.core.common._reload import reload, self_reload
from taipy.core.common._unicode_to_python_variable_name import _protect_name
from taipy.core.common.alias import ScenarioId
from taipy.core.cycle.cycle import Cycle
from taipy.core.pipeline.pipeline import Pipeline


class Scenario:
    """
    Represents an instance of the  business case to solve.

    It holds a set of pipelines to submit for execution in order to solve the business case.

    Attributes:
        config_id (str): Identifier of the scenario configuration.
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

    ID_PREFIX = "SCENARIO"
    __SEPARATOR = "_"

    def __init__(
        self,
        config_id: str,
        pipelines: List[Pipeline],
        properties: Dict[str, Any],
        scenario_id: ScenarioId = None,
        creation_date=None,
        is_master: bool = False,
        cycle: Cycle = None,
        subscribers: Set[Callable] = None,
        tags: Set[str] = None,
    ):
        self.config_id = _protect_name(config_id)
        self.id: ScenarioId = scenario_id or self.new_id(self.config_id)
        self.pipelines = {p.config_id: p for p in pipelines}
        self.creation_date = creation_date or datetime.now()
        self.cycle = cycle

        self._subscribers = subscribers or set()
        self._master_scenario = is_master
        self._tags = tags or set()

        self._properties = _Properties(self, **properties)

    def __getstate__(self):
        return self.id

    def __setstate__(self, id):
        from taipy.core.scenario.scenario_manager import ScenarioManager

        sc = ScenarioManager._get(id)
        self.__dict__ = sc.__dict__

    @property  # type: ignore
    @self_reload("scenario")
    def is_master(self):
        return self._master_scenario

    @property  # type: ignore
    @self_reload("scenario")
    def subscribers(self):
        return self._subscribers

    @property  # type: ignore
    @self_reload("scenario")
    def tags(self):
        return self._tags

    @property  # type: ignore
    def properties(self):
        self._properties = reload("scenario", self)._properties
        return self._properties

    def __eq__(self, other):
        return self.id == other.id

    @staticmethod
    def new_id(config_id: str) -> ScenarioId:
        """Generates a unique scenario identifier."""
        return ScenarioId(Scenario.__SEPARATOR.join([Scenario.ID_PREFIX, _protect_name(config_id), str(uuid.uuid4())]))

    def __getattr__(self, attribute_name):
        protected_attribute_name = _protect_name(attribute_name)
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
        raise AttributeError(f"{attribute_name} is not an attribute of scenario {self.id}")

    def add_subscriber(self, callback: Callable):
        """Adds callback function to be called when executing the scenario each time a scenario job changes status."""
        self._subscribers = reload("scenario", self)._subscribers
        self._subscribers.add(callback)

    def add_tag(self, tag: str):
        """Adds tag to the set of tags."""
        self._tags = reload("scenario", self)._tags
        self._tags.add(tag)

    def has_tag(self, tag: str) -> bool:
        return tag in self.tags

    def remove_subscriber(self, callback: Callable):
        """Removes callback function."""
        self._subscribers = reload("scenario", self)._subscribers
        self._subscribers.remove(callback)

    def remove_tag(self, tag: str):
        """Removes tag."""
        self._tags = reload("scenario", self)._tags
        if self.has_tag(tag):
            self._tags.remove(tag)
