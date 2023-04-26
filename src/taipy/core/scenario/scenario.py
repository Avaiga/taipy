# Copyright 2023 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

from __future__ import annotations

import pathlib
import uuid
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Set, Union

from taipy.config.common._template_handler import _TemplateHandler as _tpl
from taipy.config.common._validate_id import _validate_id

from .._entity._entity import _Entity
from .._entity._labeled import _Labeled
from .._entity._properties import _Properties
from .._entity._reload import _reload, _self_reload, _self_setter
from .._entity._submittable import _Submittable
from .._version._version_manager_factory import _VersionManagerFactory
from ..common._listattributes import _ListAttributes
from ..common._utils import _Subscriber
from ..cycle.cycle import Cycle
from ..data.data_node import DataNode
from ..exceptions.exceptions import NonExistingPipeline
from ..job.job import Job
from ..pipeline._pipeline_manager_factory import _PipelineManagerFactory
from ..pipeline.pipeline import Pipeline
from ..pipeline.pipeline_id import PipelineId
from ..task.task import Task
from .scenario_id import ScenarioId


class Scenario(_Entity, _Submittable, _Labeled):
    """Instance of a Business case to solve.

    A scenario holds a list of pipelines (instances of `Pipeline^` class) to submit for execution
    in order to solve the Business case.

    Attributes:
        config_id (str): The identifier of the `ScenarioConfig^`.
        pipelines (List[Pipeline^]): The list of pipelines.
        properties (dict[str, Any]): A dictionary of additional properties.
        scenario_id (str): The unique identifier of this scenario.
        creation_date (datetime): The date and time of the scenario's creation.
        is_primary (bool): True if the scenario is the primary of its cycle. False otherwise.
        cycle (Cycle^): The cycle of the scenario.
        subscribers (Set[Callable]): The set of callbacks to be called on `Job^`'s status change.
        tags (Set[str]): The list of scenario's tags.
        version (str): The string indicates the application version of the scenario to instantiate. If not provided,
            the latest version is used.
    """

    _ID_PREFIX = "SCENARIO"
    _MANAGER_NAME = "scenario"
    __SEPARATOR = "_"

    def __init__(
        self,
        config_id: str,
        pipelines: Union[List[PipelineId], List[Pipeline]],
        properties: Dict[str, Any],
        scenario_id: Optional[ScenarioId] = None,
        creation_date: Optional[datetime] = None,
        is_primary: bool = False,
        cycle: Optional[Cycle] = None,
        subscribers: Optional[List[_Subscriber]] = None,
        tags: Optional[Set[str]] = None,
        version: str = None,
    ):
        super().__init__(subscribers)
        self.config_id = _validate_id(config_id)
        self.id: ScenarioId = scenario_id or self._new_id(self.config_id)
        self._pipelines = pipelines
        self._creation_date = creation_date or datetime.now()
        self._cycle = cycle
        self._primary_scenario = is_primary
        self._tags = tags or set()
        self._properties = _Properties(self, **properties)
        self._version = version or _VersionManagerFactory._build_manager()._get_latest_version()

    @staticmethod
    def _new_id(config_id: str) -> ScenarioId:
        """Generate a unique scenario identifier."""
        return ScenarioId(Scenario.__SEPARATOR.join([Scenario._ID_PREFIX, _validate_id(config_id), str(uuid.uuid4())]))

    def __getstate__(self):
        return self.id

    def __setstate__(self, id):
        from ... import core as tp

        sc = tp.get(id)
        self.__dict__ = sc.__dict__

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id

    def __getattr__(self, attribute_name):
        protected_attribute_name = _validate_id(attribute_name)
        if protected_attribute_name in self._properties:
            return _tpl._replace_templates(self._properties[protected_attribute_name])
        pipelines = self.pipelines
        if protected_attribute_name in pipelines:
            return pipelines[protected_attribute_name]
        for pipeline in pipelines.values():
            tasks = pipeline.tasks
            if protected_attribute_name in tasks:
                return tasks[protected_attribute_name]
            for task in tasks.values():
                if protected_attribute_name in task.input:
                    return task.input[protected_attribute_name]
                if protected_attribute_name in task.output:
                    return task.output[protected_attribute_name]
        raise AttributeError(f"{attribute_name} is not an attribute of scenario {self.id}")

    @property  # type: ignore
    @_self_reload(_MANAGER_NAME)
    def pipelines(self):
        return self.__get_pipelines()

    @pipelines.setter  # type: ignore
    @_self_setter(_MANAGER_NAME)
    def pipelines(self, pipelines: Union[List[PipelineId], List[Pipeline]]):
        self._pipelines = pipelines

    @property
    def tasks(self) -> Dict[str, List[Task]]:
        tasks: Dict[str, List[Task]] = {}
        list_dict_tasks = [pipeline.tasks for pipeline in self.pipelines.values()]
        for dict_task in list_dict_tasks:
            for task_config_id, task in dict_task.items():
                if task_config_id in tasks:
                    if task not in tasks[task_config_id]:
                        tasks[task_config_id].append(task)
                else:
                    tasks[task_config_id] = [task]
        return tasks

    def _get_set_of_tasks(self) -> Set[Task]:
        tasks = set()
        list_dict_tasks = [pipeline.tasks for pipeline in self.pipelines.values()]
        for dict_task in list_dict_tasks:
            for task in dict_task.values():
                tasks.add(task)
        return tasks

    @property
    def data_nodes(self) -> Dict[str, DataNode]:
        data_nodes = {}
        list_data_nodes = [pipeline.data_nodes for pipeline in self.pipelines.values()]
        for data_node in list_data_nodes:
            for k, v in data_node.items():
                data_nodes[k] = v
        return data_nodes

    @property  # type: ignore
    @_self_reload(_MANAGER_NAME)
    def creation_date(self):
        return self._creation_date

    @creation_date.setter  # type: ignore
    @_self_setter(_MANAGER_NAME)
    def creation_date(self, val):
        self._creation_date = val

    @property  # type: ignore
    @_self_reload(_MANAGER_NAME)
    def cycle(self):
        return self._cycle

    @cycle.setter  # type: ignore
    @_self_setter(_MANAGER_NAME)
    def cycle(self, val):
        self._cycle = val

    @property  # type: ignore
    @_self_reload(_MANAGER_NAME)
    def is_primary(self):
        return self._primary_scenario

    @is_primary.setter  # type: ignore
    @_self_setter(_MANAGER_NAME)
    def is_primary(self, val):
        self._primary_scenario = val

    @property  # type: ignore
    @_self_reload(_MANAGER_NAME)
    def subscribers(self):
        return self._subscribers

    @subscribers.setter  # type: ignore
    @_self_setter(_MANAGER_NAME)
    def subscribers(self, val):
        self._subscribers = _ListAttributes(self, val)

    @property  # type: ignore
    @_self_reload(_MANAGER_NAME)
    def tags(self):
        return self._tags

    @tags.setter  # type: ignore
    @_self_setter(_MANAGER_NAME)
    def tags(self, val):
        self._tags = val or set()

    @property
    def version(self):
        return self._version

    @property
    def owner_id(self):
        return self._cycle.id

    @property
    def properties(self):
        self._properties = _reload(self._MANAGER_NAME, self)._properties
        return self._properties

    @property  # type: ignore
    @_self_reload(_MANAGER_NAME)
    def name(self) -> Optional[str]:
        return self._properties.get("name")

    @name.setter  # type: ignore
    @_self_setter(_MANAGER_NAME)
    def name(self, val):
        self._properties["name"] = val

    def has_tag(self, tag: str) -> bool:
        """Indicate if the scenario has a given tag.

        Parameters:
            tag (str): The tag to search among the set of scenario's tags.
        Returns:
            True if the scenario has the tag given as parameter. False otherwise.
        """
        return tag in self.tags

    def _add_tag(self, tag: str):
        self._tags = _reload("scenario", self)._tags
        self._tags.add(tag)

    def _remove_tag(self, tag: str):
        self._tags = _reload("scenario", self)._tags
        if self.has_tag(tag):
            self._tags.remove(tag)

    def subscribe(
        self,
        callback: Callable[[Scenario, Job], None],
        params: Optional[List[Any]] = None,
    ):
        """Subscribe a function to be called on `Job^` status change.

        The subscription is applied to all jobs created from the scenario's execution.

        Parameters:
            callback (Callable[[Scenario^, Job^], None]): The callable function to be called
                on status change.
            params (Optional[List[Any]]): The parameters to be passed to the _callback_.

        Note:
            Notification will be available only for jobs created after this subscription.
        """
        from ... import core as tp

        return tp.subscribe_scenario(callback, params, self)

    def unsubscribe(self, callback: Callable[[Scenario, Job], None], params: Optional[List[Any]] = None):
        """Unsubscribe a function that is called when the status of a `Job^` changes.

        Parameters:
            callback (Callable[[Scenario^, Job^], None]): The callable function to unsubscribe.
            params (Optional[List[Any]]): The parameters to be passed to the _callback_.

        Note:
            The function will continue to be called for ongoing jobs.
        """
        from ... import core as tp

        return tp.unsubscribe_scenario(callback, params, self)

    def submit(
        self,
        callbacks: Optional[List[Callable]] = None,
        force: bool = False,
        wait: bool = False,
        timeout: Optional[Union[float, int]] = None,
    ) -> List[Job]:
        """Submit this scenario for execution.

        All the `Task^`s of the scenario will be submitted for execution.

        Parameters:
            callbacks (List[Callable]): The list of callable functions to be called on status
                change.
            force (bool): Force execution even if the data nodes are in cache.
            wait (bool): Wait for the orchestrated jobs created from the scenario submission to be finished in
                asynchronous mode.
            timeout (Union[float, int]): The optional maximum number of seconds to wait for the jobs to be finished
                before returning.

        Returns:
            A list of created `Job^`s.
        """
        from ._scenario_manager_factory import _ScenarioManagerFactory

        return _ScenarioManagerFactory._build_manager()._submit(self, callbacks, force, wait, timeout)

    def export(
        self,
        folder_path: Union[str, pathlib.Path],
    ):
        """Export all related entities of this scenario to a folder.

        Parameters:
            folder_path (Union[str, pathlib.Path]): The folder path to export the scenario to.
        """
        from ... import core as tp

        return tp.export_scenario(self.id, folder_path)

    def set_primary(self):
        """Promote the scenario as the primary scenario of its cycle.

        If the cycle already has a primary scenario, it will be demoted, and it will no longer
        be primary for the cycle.
        """
        from ... import core as tp

        return tp.set_primary(self)

    def add_tag(self, tag: str):
        """Add a tag to this scenario.

        If the scenario's cycle already have another scenario tagged with _tag_ the other
        scenario will be untagged.

        Parameters:
            tag (str): The tag to add to this scenario.
        """
        from ... import core as tp

        return tp.tag(self, tag)

    def remove_tag(self, tag: str):
        """Remove a tag from this scenario.

        Parameters:
            tag (str): The tag to remove from the set of the scenario's tags.
        """
        from ... import core as tp

        return tp.untag(self, tag)

    def __get_pipelines(self):
        pipelines = {}
        pipeline_manager = _PipelineManagerFactory._build_manager()

        for pipeline_or_id in self._pipelines:
            p = pipeline_manager._get(pipeline_or_id, pipeline_or_id)

            if not isinstance(p, Pipeline):
                raise NonExistingPipeline(pipeline_or_id)
            pipelines[p.config_id] = p
        return pipelines

    def get_label(self) -> str:
        """Returns the scenario simple label prefixed by its owner label.

        Returns:
            The label of the scenario as a string.
        """
        return self._get_label()

    def get_simple_label(self) -> str:
        """Returns the scenario simple label.

        Returns:
            The simple label of the scenario as a string.
        """
        return self._get_simple_label()
