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

import datetime
from functools import partial
from typing import Any, Callable, List, Optional, Union

from taipy.config import Config

from .._entity._entity_ids import _EntityIds
from .._manager._manager import _Manager
from .._repository._abstract_repository import _AbstractRepository
from .._version._version_mixin import _VersionMixin
from ..common.warn_if_inputs_not_ready import _warn_if_inputs_not_ready
from ..config.scenario_config import ScenarioConfig
from ..cycle._cycle_manager_factory import _CycleManagerFactory
from ..cycle.cycle import Cycle
from ..data._data_manager_factory import _DataManagerFactory
from ..exceptions.exceptions import (
    DeletingPrimaryScenario,
    DifferentScenarioConfigs,
    DoesNotBelongToACycle,
    InsufficientScenarioToCompare,
    InvalidSequence,
    InvalidSscenario,
    NonExistingComparator,
    NonExistingScenario,
    NonExistingScenarioConfig,
    SequenceTaskConfigDoesNotExistInSameScenarioConfig,
    UnauthorizedTagError,
)
from ..job._job_manager_factory import _JobManagerFactory
from ..job.job import Job
from ..notification import EventEntityType, EventOperation, _publish_event
from ..task._task_manager_factory import _TaskManagerFactory
from .scenario import Scenario
from .scenario_id import ScenarioId


class _ScenarioManager(_Manager[Scenario], _VersionMixin):
    _AUTHORIZED_TAGS_KEY = "authorized_tags"
    _ENTITY_NAME = Scenario.__name__
    _EVENT_ENTITY_TYPE = EventEntityType.SCENARIO

    _repository: _AbstractRepository

    @classmethod
    def _get_all(cls, version_number: Optional[str] = None) -> List[Scenario]:
        """
        Returns all entities.
        """
        filters = cls._build_filters_with_version(version_number)
        return cls._repository._load_all(filters)

    @classmethod
    def _subscribe(
        cls,
        callback: Callable[[Scenario, Job], None],
        params: Optional[List[Any]] = None,
        scenario: Optional[Scenario] = None,
    ):
        if scenario is None:
            scenarios = cls._get_all()
            for scn in scenarios:
                cls.__add_subscriber(callback, params, scn)
            return

        cls.__add_subscriber(callback, params, scenario)

    @classmethod
    def _unsubscribe(
        cls,
        callback: Callable[[Scenario, Job], None],
        params: Optional[List[Any]] = None,
        scenario: Optional[Scenario] = None,
    ):
        if scenario is None:
            scenarios = cls._get_all()
            for scn in scenarios:
                cls.__remove_subscriber(callback, params, scn)
            return

        cls.__remove_subscriber(callback, params, scenario)

    @classmethod
    def __add_subscriber(cls, callback, params, scenario: Scenario):
        scenario._add_subscriber(callback, params)
        _publish_event(cls._EVENT_ENTITY_TYPE, scenario.id, EventOperation.UPDATE, "subscribers")

    @classmethod
    def __remove_subscriber(cls, callback, params, scenario: Scenario):
        scenario._remove_subscriber(callback, params)
        _publish_event(cls._EVENT_ENTITY_TYPE, scenario.id, EventOperation.UPDATE, "subscribers")

    @classmethod
    def _create(
        cls,
        config: ScenarioConfig,
        creation_date: Optional[datetime.datetime] = None,
        name: Optional[str] = None,
    ) -> Scenario:
        _task_manager = _TaskManagerFactory._build_manager()
        _data_manager = _DataManagerFactory._build_manager()

        scenario_id = Scenario._new_id(str(config.id))
        cycle = (
            _CycleManagerFactory._build_manager()._get_or_create(config.frequency, creation_date)
            if config.frequency
            else None
        )
        cycle_id = cycle.id if cycle else None
        tasks = (
            _task_manager._bulk_get_or_create(config.task_configs, cycle_id, scenario_id) if config.task_configs else []
        )
        additional_data_nodes = (
            _data_manager._bulk_get_or_create(config.additional_data_node_configs, cycle_id, scenario_id)
            if config.additional_data_node_configs
            else {}
        )

        sequences = {}
        tasks_and_config_id_maps = {task.config_id: task for task in tasks}
        for sequence_name, sequence_task_configs in config.sequences.items():
            sequence_tasks = []
            non_existing_sequence_task_config_in_scenario_config = set()
            for sequence_task_config in sequence_task_configs:
                if task := tasks_and_config_id_maps.get(sequence_task_config.id):
                    sequence_tasks.append(task)
                else:
                    non_existing_sequence_task_config_in_scenario_config.add(sequence_task_config.id)
            if len(non_existing_sequence_task_config_in_scenario_config) > 0:
                raise SequenceTaskConfigDoesNotExistInSameScenarioConfig(
                    list(non_existing_sequence_task_config_in_scenario_config), sequence_name, str(config.id)
                )
            sequences[sequence_name] = {Scenario._SEQUENCE_TASKS_KEY: sequence_tasks}

        is_primary_scenario = len(cls._get_all_by_cycle(cycle)) == 0 if cycle else False
        props = config._properties.copy()
        if name:
            props["name"] = name
        version = cls._get_latest_version()

        scenario = Scenario(
            config_id=str(config.id),
            tasks=set(tasks),
            properties=props,
            additional_data_nodes=set(additional_data_nodes.values()),
            scenario_id=scenario_id,
            creation_date=creation_date,
            is_primary=is_primary_scenario,
            cycle=cycle,
            version=version,
            sequences=sequences,
        )

        for task in tasks:
            if scenario_id not in task._parent_ids:
                task._parent_ids.update([scenario_id])
                _task_manager._set(task)

        for dn in additional_data_nodes.values():
            if scenario_id not in dn._parent_ids:
                dn._parent_ids.update([scenario_id])
                _data_manager._set(dn)

        cls._set(scenario)

        if not scenario._is_consistent():
            raise InvalidSscenario(scenario.id)

        actual_sequences = scenario._get_sequences()
        for sequence_name in sequences.keys():
            if not actual_sequences[sequence_name]._is_consistent():
                raise InvalidSequence(actual_sequences[sequence_name].id)

        _publish_event(cls._EVENT_ENTITY_TYPE, scenario.id, EventOperation.CREATION, None)
        return scenario

    @classmethod
    def _is_submittable(cls, scenario: Union[Scenario, ScenarioId]) -> bool:
        if isinstance(scenario, str):
            scenario = cls._get(scenario)
        return isinstance(scenario, Scenario)

    @classmethod
    def _submit(
        cls,
        scenario: Union[Scenario, ScenarioId],
        callbacks: Optional[List[Callable]] = None,
        force: bool = False,
        wait: bool = False,
        timeout: Optional[Union[float, int]] = None,
        check_inputs_are_ready: bool = True,
    ) -> List[Job]:
        scenario_id = scenario.id if isinstance(scenario, Scenario) else scenario
        scenario = cls._get(scenario_id)
        if scenario is None:
            raise NonExistingScenario(scenario_id)
        callbacks = callbacks or []
        scenario_subscription_callback = cls.__get_status_notifier_callbacks(scenario) + callbacks
        if check_inputs_are_ready:
            _warn_if_inputs_not_ready(scenario.get_inputs())

        jobs = (
            _TaskManagerFactory._build_manager()
            ._orchestrator()
            .submit(scenario, callbacks=scenario_subscription_callback, force=force, wait=wait, timeout=timeout)
        )
        _publish_event(cls._EVENT_ENTITY_TYPE, scenario.id, EventOperation.SUBMISSION, None)
        return jobs

    @classmethod
    def __get_status_notifier_callbacks(cls, scenario: Scenario) -> List:
        return [partial(c.callback, *c.params, scenario) for c in scenario.subscribers]

    @classmethod
    def _get_primary(cls, cycle: Cycle) -> Optional[Scenario]:
        scenarios = cls._get_all_by_cycle(cycle)
        for scenario in scenarios:
            if scenario.is_primary:
                return scenario
        return None

    @classmethod
    def _get_by_tag(cls, cycle: Cycle, tag: str) -> Optional[Scenario]:
        scenarios = cls._get_all_by_cycle(cycle)
        for scenario in scenarios:
            if scenario.has_tag(tag):
                return scenario
        return None

    @classmethod
    def _get_all_by_tag(cls, tag: str) -> List[Scenario]:
        scenarios = []
        for scenario in cls._get_all():
            if scenario.has_tag(tag):
                scenarios.append(scenario)
        return scenarios

    @classmethod
    def _get_all_by_cycle(cls, cycle: Cycle) -> List[Scenario]:
        filters = cls._build_filters_with_version("all")

        if not filters:
            filters = [{}]
        for fil in filters:
            fil.update({"cycle": cycle.id})
        return cls._get_all_by(filters)

    @classmethod
    def _get_primary_scenarios(cls) -> List[Scenario]:
        primary_scenarios = []
        for scenario in cls._get_all():
            if scenario.is_primary:
                primary_scenarios.append(scenario)
        return primary_scenarios

    @classmethod
    def _is_promotable_to_primary(cls, scenario: Union[Scenario, ScenarioId]) -> bool:
        if isinstance(scenario, str):
            scenario = cls._get(scenario)
        if scenario and not scenario.is_primary and scenario.cycle:
            return True
        return False

    @classmethod
    def _set_primary(cls, scenario: Scenario):
        if scenario.cycle:
            primary_scenario = cls._get_primary(scenario.cycle)
            # To prevent SAME scenario updating out of Context Manager
            if primary_scenario and primary_scenario != scenario:
                primary_scenario.is_primary = False  # type: ignore
            scenario.is_primary = True  # type: ignore
        else:
            raise DoesNotBelongToACycle(
                f"Can't set scenario {scenario.id} to primary because it doesn't belong to a cycle."
            )

    @classmethod
    def _tag(cls, scenario: Scenario, tag: str):
        tags = scenario.properties.get(cls._AUTHORIZED_TAGS_KEY, set())
        if len(tags) > 0 and tag not in tags:
            raise UnauthorizedTagError(f"Tag `{tag}` not authorized by scenario configuration `{scenario.config_id}`")
        if scenario.cycle:
            old_tagged_scenario = cls._get_by_tag(scenario.cycle, tag)
            if old_tagged_scenario:
                old_tagged_scenario.remove_tag(tag)
                cls._set(old_tagged_scenario)
        scenario._add_tag(tag)
        cls._set(scenario)
        _publish_event(cls._EVENT_ENTITY_TYPE, scenario.id, EventOperation.UPDATE, "tags")

    @classmethod
    def _untag(cls, scenario: Scenario, tag: str):
        scenario._remove_tag(tag)
        cls._set(scenario)
        _publish_event(cls._EVENT_ENTITY_TYPE, scenario.id, EventOperation.UPDATE, "tags")

    @classmethod
    def _compare(cls, *scenarios: Scenario, data_node_config_id: Optional[str] = None):
        if len(scenarios) < 2:
            raise InsufficientScenarioToCompare("At least two scenarios are required to compare.")

        if not all(scenarios[0].config_id == scenario.config_id for scenario in scenarios):
            raise DifferentScenarioConfigs("Scenarios to compare must have the same configuration.")

        if scenario_config := _ScenarioManager.__get_config(scenarios[0]):
            results = {}
            if data_node_config_id:
                if data_node_config_id in scenario_config.comparators.keys():
                    dn_comparators = {data_node_config_id: scenario_config.comparators[data_node_config_id]}
                else:
                    raise NonExistingComparator(f"Data node config {data_node_config_id} has no comparator.")
            else:
                dn_comparators = scenario_config.comparators

            for data_node_config_id, comparators in dn_comparators.items():
                data_nodes = [scenario.__getattr__(data_node_config_id).read() for scenario in scenarios]
                results[data_node_config_id] = {
                    comparator.__name__: comparator(*data_nodes) for comparator in comparators
                }

            return results

        else:
            raise NonExistingScenarioConfig(scenarios[0].config_id)

    @staticmethod
    def __get_config(scenario: Scenario):
        return Config.scenarios.get(scenario.config_id, None)

    @classmethod
    def _is_deletable(cls, scenario: Union[Scenario, ScenarioId]) -> bool:
        if isinstance(scenario, str):
            scenario = cls._get(scenario)
        if scenario.is_primary:
            if len(cls._get_all_by_cycle(scenario.cycle)) > 1:
                return False
        return True

    @classmethod
    def _delete(cls, scenario_id: ScenarioId):
        scenario = cls._get(scenario_id)
        if not cls._is_deletable(scenario):
            raise DeletingPrimaryScenario(
                f"Scenario {scenario.id}, which has config id {scenario.config_id}, is primary and there are "
                f"other scenarios in the same cycle. "
            )
        if scenario.is_primary:
            _CycleManagerFactory._build_manager()._delete(scenario.cycle.id)
        super()._delete(scenario_id)

    @classmethod
    def _hard_delete(cls, scenario_id: ScenarioId):
        scenario = cls._get(scenario_id)
        if not cls._is_deletable(scenario):
            raise DeletingPrimaryScenario(
                f"Scenario {scenario.id}, which has config id {scenario.config_id}, is primary and there are "
                f"other scenarios in the same cycle. "
            )
        if scenario.is_primary:
            _CycleManagerFactory._build_manager()._hard_delete(scenario.cycle.id)
        else:
            entity_ids_to_delete = cls._get_children_entity_ids(scenario)
            entity_ids_to_delete.scenario_ids.add(scenario.id)
            cls._delete_entities_of_multiple_types(entity_ids_to_delete)

    @classmethod
    def _delete_by_version(cls, version_number: str):
        """
        Deletes scenario by the version number.

        Check if the cycle is only attached to this scenario, then delete it.
        """
        for scenario in cls._repository._search("version", version_number):
            if scenario.cycle and len(cls._get_all_by_cycle(scenario.cycle)) == 1:
                _CycleManagerFactory._build_manager()._delete(scenario.cycle.id)
            super()._delete(scenario.id)

    @classmethod
    def _get_children_entity_ids(cls, scenario: Scenario) -> _EntityIds:
        entity_ids = _EntityIds()
        for sequence in scenario.sequences.values():
            if sequence.owner_id == scenario.id:
                entity_ids.sequence_ids.add(sequence.id)
        for task in scenario.tasks.values():
            if task.owner_id == scenario.id:
                entity_ids.task_ids.add(task.id)
        for data_node in scenario.data_nodes.values():
            if data_node.owner_id == scenario.id:
                entity_ids.data_node_ids.add(data_node.id)

        jobs = _JobManagerFactory._build_manager()._get_all()
        for job in jobs:
            if job.task.id in entity_ids.task_ids:
                entity_ids.job_ids.add(job.id)

        return entity_ids

    @classmethod
    def _get_by_config_id(cls, config_id: str, version_number: Optional[str] = None) -> List[Scenario]:
        """
        Get all scenarios by its config id.
        """
        filters = cls._build_filters_with_version(version_number)
        if not filters:
            filters = [{}]
        for fil in filters:
            fil.update({"config_id": config_id})
        return cls._repository._load_all(filters)
