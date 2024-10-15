# Copyright 2021-2024 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

from datetime import datetime
from functools import partial
from typing import Any, Callable, Dict, List, Literal, Optional, Union

from taipy.common.config import Config

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
    InvalidScenario,
    NonExistingComparator,
    NonExistingScenario,
    NonExistingScenarioConfig,
    SequenceTaskConfigDoesNotExistInSameScenarioConfig,
    UnauthorizedTagError,
)
from ..job._job_manager_factory import _JobManagerFactory
from ..job.job import Job
from ..notification import EventEntityType, EventOperation, Notifier, _make_event
from ..reason import (
    EntityDoesNotExist,
    EntityIsNotAScenario,
    EntityIsNotSubmittableEntity,
    ReasonCollection,
    ScenarioDoesNotBelongToACycle,
    ScenarioIsThePrimaryScenario,
    WrongConfigType,
)
from ..submission._submission_manager_factory import _SubmissionManagerFactory
from ..submission.submission import Submission
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
    ) -> None:
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
    ) -> None:
        if scenario is None:
            scenarios = cls._get_all()
            for scn in scenarios:
                cls.__remove_subscriber(callback, params, scn)
            return

        cls.__remove_subscriber(callback, params, scenario)

    @classmethod
    def __add_subscriber(cls, callback, params, scenario: Scenario) -> None:
        scenario._add_subscriber(callback, params)
        Notifier.publish(
            _make_event(scenario, EventOperation.UPDATE, attribute_name="subscribers", attribute_value=params)
        )

    @classmethod
    def __remove_subscriber(cls, callback, params, scenario: Scenario) -> None:
        scenario._remove_subscriber(callback, params)
        Notifier.publish(
            _make_event(scenario, EventOperation.UPDATE, attribute_name="subscribers", attribute_value=params)
        )

    @classmethod
    def _can_create(cls, config: Optional[ScenarioConfig] = None) -> ReasonCollection:
        config_id = getattr(config, "id", None) or str(config)
        reason_collector = ReasonCollection()

        if config is not None and not isinstance(config, ScenarioConfig):
            reason_collector._add_reason(config_id, WrongConfigType(config_id, ScenarioConfig.__name__))

        return reason_collector

    @classmethod
    def _create(
        cls,
        config: ScenarioConfig,
        creation_date: Optional[datetime] = None,
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
            if non_existing_sequence_task_config_in_scenario_config:
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
            raise InvalidScenario(scenario.id)

        from ..sequence._sequence_manager_factory import _SequenceManagerFactory

        _SequenceManagerFactory._build_manager()._bulk_create_from_scenario(scenario)

        Notifier.publish(_make_event(scenario, EventOperation.CREATION))
        return scenario

    @classmethod
    def _is_submittable(cls, scenario: Union[Scenario, ScenarioId]) -> ReasonCollection:
        reason_collector = ReasonCollection()

        if isinstance(scenario, str):
            scenario_id = scenario
            scenario = cls._get(scenario)
            if scenario is None:
                reason_collector._add_reason(scenario_id, EntityDoesNotExist(scenario_id))
                return reason_collector

        if not isinstance(scenario, Scenario):
            reason_collector._add_reason(str(scenario), EntityIsNotSubmittableEntity(str(scenario)))
        else:
            return scenario.is_ready_to_run()

        return reason_collector

    @classmethod
    def _submit(
        cls,
        scenario: Union[Scenario, ScenarioId],
        callbacks: Optional[List[Callable]] = None,
        force: bool = False,
        wait: bool = False,
        timeout: Optional[Union[float, int]] = None,
        check_inputs_are_ready: bool = True,
        **properties,
    ) -> Submission:
        scenario_id = scenario.id if isinstance(scenario, Scenario) else scenario
        if not isinstance(scenario, Scenario):
            scenario = cls._get(scenario_id)
        if scenario is None or not cls._exists(scenario_id):
            raise NonExistingScenario(scenario_id)
        callbacks = callbacks or []
        scenario_subscription_callback = cls.__get_status_notifier_callbacks(scenario) + callbacks
        if check_inputs_are_ready:
            _warn_if_inputs_not_ready(scenario.get_inputs())

        submission = (
            _TaskManagerFactory._build_manager()
            ._orchestrator()
            .submit(
                scenario,
                callbacks=scenario_subscription_callback,
                force=force,
                wait=wait,
                timeout=timeout,
                **properties,
            )
        )
        Notifier.publish(_make_event(scenario, EventOperation.SUBMISSION))
        return submission

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
    def _get_all_by_cycle_tag(cls, cycle: Cycle, tag: str) -> List[Scenario]:
        cycles_scenarios = cls._get_all_by_cycle(cycle)
        return [scenario for scenario in cycles_scenarios if scenario.has_tag(tag)]

    @classmethod
    def _get_all_by_tag(cls, tag: str) -> List[Scenario]:
        return [scenario for scenario in cls._get_all() if scenario.has_tag(tag)]

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
        return [scenario for scenario in cls._get_all() if scenario.is_primary]

    @staticmethod
    def _sort_scenarios(
        scenarios: List[Scenario],
        descending: bool = False,
        sort_key: Literal["name", "id", "config_id", "creation_date", "tags"] = "name",
    ) -> List[Scenario]:
        if sort_key in ["name", "config_id", "creation_date", "tags"]:
            if sort_key == "tags":
                scenarios.sort(key=lambda x: (tuple(sorted(x.tags)), x.id), reverse=descending)
            else:
                scenarios.sort(key=lambda x: (getattr(x, sort_key), x.id), reverse=descending)
        elif sort_key == "id":
            scenarios.sort(key=lambda x: x.id, reverse=descending)
        else:
            scenarios.sort(key=lambda x: (x.name, x.id), reverse=descending)
        return scenarios

    @staticmethod
    def _filter_by_creation_time(
        scenarios: List[Scenario],
        created_start_time: Optional[datetime] = None,
        created_end_time: Optional[datetime] = None,
    ) -> List[Scenario]:
        """
        Filter a list of scenarios by a given creation time period.

        Parameters:
            created_start_time (Optional[datetime]): Start time of the period. The start time is inclusive.
            created_end_time (Optional[datetime]): End time of the period. The end time is exclusive.

        Returns:
            List[Scenario]: List of scenarios created in the given time period.
        """
        if not created_start_time and not created_end_time:
            return scenarios

        if not created_start_time:
            return [scenario for scenario in scenarios if scenario.creation_date < created_end_time]

        if not created_end_time:
            return [scenario for scenario in scenarios if created_start_time <= scenario.creation_date]

        return [scenario for scenario in scenarios if created_start_time <= scenario.creation_date < created_end_time]

    @classmethod
    def _is_promotable_to_primary(cls, scenario: Union[Scenario, ScenarioId]) -> ReasonCollection:
        reason_collection = ReasonCollection()

        if isinstance(scenario, str):
            scenario_id = scenario
            scenario = cls._get(scenario_id)
        else:
            scenario_id = scenario.id

        if not scenario:
            reason_collection._add_reason(scenario_id, EntityDoesNotExist(scenario_id))
        else:
            if scenario.is_primary:
                reason_collection._add_reason(scenario_id, ScenarioIsThePrimaryScenario(scenario_id, scenario.cycle.id))

            if not scenario.cycle:
                reason_collection._add_reason(scenario_id, ScenarioDoesNotBelongToACycle(scenario_id))

        return reason_collection

    @classmethod
    def _set_primary(cls, scenario: Scenario) -> None:
        if not scenario.cycle:
            raise DoesNotBelongToACycle(
                f"Can't set scenario {scenario.id} to primary because it doesn't belong to a cycle."
            )

        primary_scenario = cls._get_primary(scenario.cycle)
        # To prevent SAME scenario updating out of Context Manager
        if primary_scenario and primary_scenario != scenario:
            primary_scenario.is_primary = False  # type: ignore
        scenario.is_primary = True  # type: ignore

    @classmethod
    def _tag(cls, scenario: Scenario, tag: str) -> None:
        tags = scenario.properties.get(cls._AUTHORIZED_TAGS_KEY, set())
        if len(tags) > 0 and tag not in tags:
            raise UnauthorizedTagError(f"Tag `{tag}` not authorized by scenario configuration `{scenario.config_id}`")
        scenario._add_tag(tag)
        cls._set(scenario)
        Notifier.publish(
            _make_event(scenario, EventOperation.UPDATE, attribute_name="tags", attribute_value=scenario.tags)
        )

    @classmethod
    def _untag(cls, scenario: Scenario, tag: str) -> None:
        scenario._remove_tag(tag)
        cls._set(scenario)
        Notifier.publish(
            _make_event(scenario, EventOperation.UPDATE, attribute_name="tags", attribute_value=scenario.tags)
        )

    @classmethod
    def _compare(cls, *scenarios: Scenario, data_node_config_id: Optional[str] = None) -> Dict:
        if len(scenarios) < 2:
            raise InsufficientScenarioToCompare("At least two scenarios are required to compare.")

        if not all(scenarios[0].config_id == scenario.config_id for scenario in scenarios):
            raise DifferentScenarioConfigs("Scenarios to compare must have the same configuration.")

        if scenario_config := cls.__get_config(scenarios[0]):
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
    def _is_deletable(cls, scenario: Union[Scenario, ScenarioId]) -> ReasonCollection:
        reason_collection = ReasonCollection()

        if isinstance(scenario, str):
            scenario_id = scenario
            scenario = cls._get(scenario)
            if scenario is None:
                reason_collection._add_reason(scenario_id, EntityDoesNotExist(scenario_id))
                return reason_collection

        if not isinstance(scenario, Scenario):
            reason_collection._add_reason(str(scenario), EntityIsNotAScenario(str(scenario)))
        elif scenario.is_primary:
            if len(cls._get_all_by_cycle(scenario.cycle)) > 1:
                reason_collection._add_reason(scenario.id, ScenarioIsThePrimaryScenario(scenario.id, scenario.cycle.id))

        return reason_collection

    @classmethod
    def _delete(cls, scenario_id: ScenarioId) -> None:
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
    def _hard_delete(cls, scenario_id: ScenarioId) -> None:
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
    def _delete_by_version(cls, version_number: str) -> None:
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

        submissions = _SubmissionManagerFactory._build_manager()._get_all()
        submitted_entity_ids = list(entity_ids.scenario_ids.union(entity_ids.sequence_ids, entity_ids.task_ids))
        for submission in submissions:
            if submission.entity_id in submitted_entity_ids or submission.entity_id == scenario.id:
                entity_ids.submission_ids.add(submission.id)

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
