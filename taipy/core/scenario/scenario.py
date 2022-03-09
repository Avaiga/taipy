from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Set

from taipy.core.common._entity import _Entity
from taipy.core.common._properties import _Properties
from taipy.core.common._reload import reload, self_reload, self_setter
from taipy.core.common._validate_id import _validate_id
from taipy.core.common.alias import ScenarioId
from taipy.core.cycle.cycle import Cycle
from taipy.core.job.job import Job
from taipy.core.pipeline.pipeline import Pipeline


class Scenario(_Entity):
    """
    Represents an instance of the  business case to solve.

    It holds a set of pipelines to submit for execution in order to solve the business case.

    Attributes:
        config_id (str): Identifier of the scenario configuration. Must be a valid Python variable name.
        pipelines (List[Pipeline]): List of pipelines.
        properties (dict): Dictionary of additional properties of the scenario.
        scenario_id (str): Unique identifier of this scenario. Will be generated if None value provided.
        creation_date (datetime): Date and time of the creation of the scenario.
        is_official (bool): True if the scenario is the official of its cycle. False otherwise.
        cycle (Cycle): Cycle of the scenario.
    """

    ID_PREFIX = "SCENARIO"
    MANAGER_NAME = "scenario"
    __SEPARATOR = "_"

    def __init__(
        self,
        config_id: str,
        pipelines: List[Pipeline],
        properties: Dict[str, Any],
        scenario_id: ScenarioId = None,
        creation_date=None,
        is_official: bool = False,
        cycle: Cycle = None,
        subscribers: Set[Callable] = None,
        tags: Set[str] = None,
    ):
        self._config_id = _validate_id(config_id)
        self.id: ScenarioId = scenario_id or self.new_id(self._config_id)
        self._pipelines = {p.config_id: p for p in pipelines}
        self._creation_date = creation_date or datetime.now()
        self._cycle = cycle
        self._subscribers = subscribers or set()
        self._official_scenario = is_official
        self._tags = tags or set()

        self._properties = _Properties(self, **properties)

    def __getstate__(self):
        return self.id

    def __setstate__(self, id):
        from taipy.core.scenario._scenario_manager import _ScenarioManager

        sc = _ScenarioManager._get(id)
        self.__dict__ = sc.__dict__

    @property  # type: ignore
    @self_reload(MANAGER_NAME)
    def config_id(self):
        return self._config_id

    @config_id.setter  # type: ignore
    @self_setter(MANAGER_NAME)
    def config_id(self, val):
        self._config_id = val

    @property  # type: ignore
    @self_reload(MANAGER_NAME)
    def pipelines(self):
        return self._pipelines

    @pipelines.setter  # type: ignore
    @self_setter(MANAGER_NAME)
    def pipelines(self, val: List[Pipeline]):
        self._pipelines = {p.config_id: p for p in val}

    @property  # type: ignore
    @self_reload(MANAGER_NAME)
    def creation_date(self):
        return self._creation_date

    @creation_date.setter  # type: ignore
    @self_setter(MANAGER_NAME)
    def creation_date(self, val):
        self._creation_date = val

    @property  # type: ignore
    @self_reload(MANAGER_NAME)
    def cycle(self):
        return self._cycle

    @cycle.setter  # type: ignore
    @self_setter(MANAGER_NAME)
    def cycle(self, val):
        self._cycle = val

    @property  # type: ignore
    @self_reload(MANAGER_NAME)
    def is_official(self):
        return self._official_scenario

    @is_official.setter  # type: ignore
    @self_setter(MANAGER_NAME)
    def is_official(self, val):
        self._official_scenario = val

    @property  # type: ignore
    @self_reload(MANAGER_NAME)
    def subscribers(self):
        return self._subscribers

    @subscribers.setter  # type: ignore
    @self_setter(MANAGER_NAME)
    def subscribers(self, val):
        self._subscribers = val or set()

    @property  # type: ignore
    @self_reload(MANAGER_NAME)
    def tags(self):
        return self._tags

    @tags.setter  # type: ignore
    @self_setter(MANAGER_NAME)
    def tags(self, val):
        self._tags = val or set()

    @property  # type: ignore
    def properties(self):
        self._properties = reload("scenario", self)._properties
        return self._properties

    def __eq__(self, other):
        return self.id == other.id

    @staticmethod
    def new_id(config_id: str) -> ScenarioId:
        """Generates a unique scenario identifier."""
        return ScenarioId(Scenario.__SEPARATOR.join([Scenario.ID_PREFIX, _validate_id(config_id), str(uuid.uuid4())]))

    def __getattr__(self, attribute_name):
        protected_attribute_name = _validate_id(attribute_name)
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

    def _add_tag(self, tag: str):
        """Adds tag to the set of tags."""
        self._tags = reload("scenario", self)._tags
        self._tags.add(tag)

    def has_tag(self, tag: str) -> bool:
        return tag in self.tags

    def remove_subscriber(self, callback: Callable):
        """Removes callback function."""
        self._subscribers = reload("scenario", self)._subscribers
        self._subscribers.remove(callback)

    def _remove_tag(self, tag: str):
        """Removes tag."""
        self._tags = reload("scenario", self)._tags
        if self.has_tag(tag):
            self._tags.remove(tag)

    def subscribe(self, callback: Callable[[Scenario, Job], None]):
        from taipy.core.scenario._scenario_manager import _ScenarioManager

        return _ScenarioManager._subscribe(callback, self)

    def unsubscribe(self, callback: Callable[[Scenario, Job], None]):
        from taipy.core.scenario._scenario_manager import _ScenarioManager

        return _ScenarioManager._unsubscribe(callback, self)

    def submit(self, force: bool = False):
        from taipy.core.scenario._scenario_manager import _ScenarioManager

        return _ScenarioManager._submit(self, force)

    def set_official(self):
        from taipy.core.scenario._scenario_manager import _ScenarioManager

        return _ScenarioManager._set_official(self)

    def add_tag(self, tag: str):
        from taipy.core.scenario._scenario_manager import _ScenarioManager

        return _ScenarioManager._tag(self, tag)

    def remove_tag(self, tag: str):
        from taipy.core.scenario._scenario_manager import _ScenarioManager

        return _ScenarioManager._untag(self, tag)
