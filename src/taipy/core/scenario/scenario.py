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
from .._entity._reload import _Reloader, _self_reload, _self_setter
from .._entity._submittable import _Submittable
from .._version._utils import _migrate_entity
from .._version._version_manager_factory import _VersionManagerFactory
from ..common import _utils
from ..common._listattributes import _ListAttributes
from ..common._utils import _Subscriber
from ..cycle._cycle_manager_factory import _CycleManagerFactory
from ..cycle.cycle import Cycle
from ..cycle.cycle_id import CycleId
from ..data._data_manager_factory import _DataManagerFactory
from ..data.data_node import DataNode
from ..data.data_node_id import DataNodeId
from ..exceptions.exceptions import NonExistingDataNode, NonExistingPipeline, NonExistingTask
from ..job.job import Job
from ..pipeline._pipeline_manager_factory import _PipelineManagerFactory
from ..pipeline.pipeline import Pipeline
from ..pipeline.pipeline_id import PipelineId
from ..task._task_manager_factory import _TaskManagerFactory
from ..task.task import Task
from ..task.task_id import TaskId
from ._scenario_model import _ScenarioModel
from .scenario_id import ScenarioId


class Scenario(_Entity, _Submittable, _Labeled):
    """Instance of a Business case to solve.

    A scenario holds a list of tasks (instances of `Task^` class) to submit for execution
    in order to solve the Business case.

    Attributes:
        config_id (str): The identifier of the `ScenarioConfig^`.
        tasks (Set[Task^]): The set of tasks.
        additional_data_nodes (Set[DataNode^]): The set of additional data nodes.
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
    _MIGRATED_PIPELINES_KEY = "pipelines"
    __SEPARATOR = "_"

    def __init__(
        self,
        config_id: str,
        tasks: Union[Set[TaskId], Set[Task]],
        properties: Dict[str, Any],
        additional_data_nodes: Optional[Union[Set[DataNodeId], Set[DataNode]]] = None,
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

        self._tasks: Union[Set[TaskId], Set[Task], Set] = set(tasks) if tasks else set()
        if not self._tasks and self._MIGRATED_PIPELINES_KEY in properties:
            self._tasks = Scenario._get_set_of_tasks_from_pipelines(
                pipelines=properties.pop(self._MIGRATED_PIPELINES_KEY, [])
            )

        self._additional_data_nodes = set(additional_data_nodes) if additional_data_nodes else set()

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

    @staticmethod
    def _get_set_of_tasks_from_pipelines(
        pipelines: Union[List[PipelineId], List[Pipeline]]
    ) -> Union[Set[Task], Set[TaskId]]:
        tasks = set()

        pipeline_manager = _PipelineManagerFactory._build_manager()

        for pipeline_or_id in pipelines:
            p = pipeline_manager._get(pipeline_or_id, pipeline_or_id)

            if not isinstance(p, Pipeline):
                raise NonExistingPipeline(pipeline_or_id)

            tasks.update(p.tasks.values())

        return tasks

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
        tasks = self.tasks
        if protected_attribute_name in tasks:
            return tasks[protected_attribute_name]
        data_nodes = self.data_nodes
        if protected_attribute_name in data_nodes:
            return data_nodes[protected_attribute_name]
        raise AttributeError(f"{attribute_name} is not an attribute of scenario {self.id}")

    # TODO: TBD
    # @property  # type: ignore
    # @_self_reload(_MANAGER_NAME)
    # def pipelines(self):
    #     return self.__get_pipelines()

    @property  # type: ignore
    @_self_reload(_MANAGER_NAME)
    def tasks(self) -> Dict[str, Task]:
        return self.__get_tasks()

    def __get_tasks(self) -> Dict[str, Task]:
        _tasks = {}
        task_manager = _TaskManagerFactory._build_manager()

        for task_or_id in self._tasks:
            t = task_manager._get(task_or_id, task_or_id)

            if not isinstance(t, Task):
                raise NonExistingTask(task_or_id)
            _tasks[t.config_id] = t
        return _tasks

    @tasks.setter  # type: ignore
    @_self_setter(_MANAGER_NAME)
    def tasks(self, val: Union[Set[TaskId], Set[Task]]):
        self._tasks = set(val)

    @property  # type: ignore
    @_self_reload(_MANAGER_NAME)
    def additional_data_nodes(self) -> Dict[str, DataNode]:
        return self.__get_additional_data_nodes()

    def __get_additional_data_nodes(self):
        additional_data_nodes = {}
        data_manager = _DataManagerFactory._build_manager()

        for dn_or_id in self._additional_data_nodes:
            dn = data_manager._get(dn_or_id, dn_or_id)

            if not isinstance(dn, DataNode):
                raise NonExistingTask(dn_or_id)
            additional_data_nodes[dn.config_id] = dn
        return additional_data_nodes

    @additional_data_nodes.setter  # type: ignore
    @_self_setter(_MANAGER_NAME)
    def additional_data_nodes(self, val: Union[Set[TaskId], Set[DataNode]]):
        self._additional_data_nodes = set(val)

    # TODO: TBD
    def _get_set_of_tasks(self) -> Set[Task]:
        tasks = set()
        list_dict_tasks = [pipeline.tasks for pipeline in self.pipelines.values()]
        for dict_task in list_dict_tasks:
            for task in dict_task.values():
                tasks.add(task)
        return tasks

    @property  # type: ignore
    @_self_reload(_MANAGER_NAME)
    def data_nodes(self) -> Dict[str, DataNode]:
        # breakpoint()
        data_nodes_dict = {dn.config_id: dn for dn in self.__get_additional_data_nodes().values()}
        for task_id, task in self.__get_tasks().items():
            data_nodes_dict.update(task.data_nodes)
        return data_nodes_dict

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

    @version.setter
    def version(self, val):
        self._version = val

    @property
    def owner_id(self):
        return self._cycle.id

    @property
    def properties(self):
        self._properties = _Reloader()._reload(self._MANAGER_NAME, self)._properties
        return self._properties

    @property  # type: ignore
    @_self_reload(_MANAGER_NAME)
    def name(self) -> Optional[str]:
        return self._properties.get("name")

    @name.setter  # type: ignore
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
        self._tags = _Reloader()._reload("scenario", self)._tags
        self._tags.add(tag)

    def _remove_tag(self, tag: str):
        self._tags = _Reloader()._reload("scenario", self)._tags
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

    def is_deletable(self) -> bool:
        """Indicate if the scenario can be deleted.

        Returns:
            True if the scenario can be deleted. False otherwise.
        """
        from ... import core as tp

        return tp.is_deletable(self)

    # TODO: TBD
    # def __get_pipelines(self):
    #     pipelines = {}
    #     pipeline_manager = _PipelineManagerFactory._build_manager()

    #     for pipeline_or_id in self._pipelines:
    #         p = pipeline_manager._get(pipeline_or_id, pipeline_or_id)

    #         if not isinstance(p, Pipeline):
    #             raise NonExistingPipeline(pipeline_or_id)
    #         pipelines[p.config_id] = p
    #     return pipelines

    @classmethod
    def _to_model(cls, entity: Scenario) -> _ScenarioModel:
        return _ScenarioModel(
            id=entity.id,
            config_id=entity.config_id,
            tasks=cls.__to_task_ids(entity._tasks),
            additional_data_nodes=cls.__to_data_node_ids(entity._additional_data_nodes),
            properties=entity._properties.data,
            creation_date=entity._creation_date.isoformat(),
            primary_scenario=entity._primary_scenario,
            subscribers=_utils._fcts_to_dict(entity._subscribers),
            tags=list(entity._tags),
            version=entity.version,
            cycle=cls.__to_cycle_id(entity._cycle),
        )

    @classmethod
    def _from_model(cls, model: _ScenarioModel):
        scenario = Scenario(
            scenario_id=model.id,
            config_id=model.config_id,
            tasks=set(model.tasks),
            additional_data_nodes=set(model.additional_data_nodes),
            properties=model.properties,
            creation_date=datetime.fromisoformat(model.creation_date),
            is_primary=model.primary_scenario,
            tags=set(model.tags),
            cycle=Scenario.__to_cycle(model.cycle),
            subscribers=[
                _Subscriber(_utils._load_fct(it["fct_module"], it["fct_name"]), it["fct_params"])
                for it in model.subscribers
            ],
            version=model.version,
        )
        return _migrate_entity(scenario)

    # TODO: TBD
    # @staticmethod
    # def __to_pipeline_ids(pipelines) -> List[PipelineId]:
    #     return [p.id if isinstance(p, Pipeline) else p for p in pipelines]

    @staticmethod
    def __to_cycle(cycle_id: Optional[CycleId] = None) -> Optional[Cycle]:
        return _CycleManagerFactory._build_manager()._get(cycle_id) if cycle_id else None

    @staticmethod
    def __to_cycle_id(cycle: Optional[Cycle] = None) -> Optional[CycleId]:
        return cycle.id if cycle else None

    @staticmethod
    def __to_task_ids(tasks) -> List[TaskId]:
        return [t.id if isinstance(t, Task) else t for t in tasks]

    @staticmethod
    def __to_data_node_ids(data_nodes) -> List[DataNodeId]:
        return [dn.id if isinstance(dn, DataNode) else dn for dn in data_nodes]

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
