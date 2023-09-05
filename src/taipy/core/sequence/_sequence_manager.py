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

import json
import pathlib
from functools import partial
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple, Union

from .._entity._entity_ids import _EntityIds
from .._manager._manager import _Manager
from .._version._version_mixin import _VersionMixin
from ..common._utils import _Subscriber
from ..common.warn_if_inputs_not_ready import _warn_if_inputs_not_ready
from ..exceptions.exceptions import (
    InvalidSequence,
    InvalidSequenceId,
    ModelNotFound,
    NonExistingSequence,
    NonExistingTask,
    SequenceBelongsToNonExistingScenario,
)
from ..job._job_manager_factory import _JobManagerFactory
from ..job.job import Job
from ..notification import EventEntityType, EventOperation, _publish_event
from ..scenario._scenario_manager_factory import _ScenarioManagerFactory
from ..scenario.scenario import Scenario
from ..scenario.scenario_id import ScenarioId
from ..task._task_manager_factory import _TaskManagerFactory
from ..task.task import Task, TaskId
from .sequence import Sequence
from .sequence_id import SequenceId


class _SequenceManager(_Manager[Sequence], _VersionMixin):

    _ENTITY_NAME = Sequence.__name__
    _EVENT_ENTITY_TYPE = EventEntityType.SEQUENCE
    _model_name = "sequences"

    @classmethod
    def _delete(cls, sequence_id: SequenceId):
        """
        Deletes a Sequence by id.
        """
        sequence_name, scenario_id = cls._breakdown_sequence_id(sequence_id)

        if scenario := _ScenarioManagerFactory._build_manager()._get(scenario_id):
            if sequence_name in scenario._sequences.keys():
                scenario.remove_sequences([sequence_name])
                if hasattr(cls, "_EVENT_ENTITY_TYPE"):
                    _publish_event(cls._EVENT_ENTITY_TYPE, sequence_id, EventOperation.DELETION, None)
                return
        raise ModelNotFound(cls._model_name, sequence_id)

    @classmethod
    def _delete_all(cls):
        """
        Deletes all Sequences.
        """
        scenarios = _ScenarioManagerFactory._build_manager()._get_all()
        for scenario in scenarios:
            scenario.sequences = {}
        if hasattr(cls, "_EVENT_ENTITY_TYPE"):
            _publish_event(cls._EVENT_ENTITY_TYPE, "all", EventOperation.DELETION, None)

    @classmethod
    def _delete_many(cls, sequence_ids: Iterable[str]):
        """
        Deletes Sequence entities by a list of Sequence ids.
        """
        scenario_manager = _ScenarioManagerFactory._build_manager()

        scenario_ids_and_sequence_names_map: Dict[str, List[str]] = {}
        for sequence in sequence_ids:
            sequence_id = sequence.id if isinstance(sequence, Sequence) else sequence
            sequence_name, scenario_id = cls._breakdown_sequence_id(sequence_id)
            sequences_names = scenario_ids_and_sequence_names_map.get(scenario_id, [])
            sequences_names.append(sequence_name)
            scenario_ids_and_sequence_names_map[scenario_id] = sequences_names

        try:
            for scenario_id, sequence_names in scenario_ids_and_sequence_names_map.items():
                scenario = scenario_manager._get(scenario_id)
                for sequence_name in sequence_names:
                    del scenario._sequences[sequence_name]
                scenario_manager._set(scenario)

            if hasattr(cls, "_EVENT_ENTITY_TYPE"):
                for sequence_id in sequence_ids:
                    _publish_event(cls._EVENT_ENTITY_TYPE, sequence_id, EventOperation.DELETION, None)
        except (ModelNotFound, KeyError):
            cls.__log_error_entity_not_found(sequence_id)
            raise ModelNotFound(cls._model_name, sequence_id)

    @classmethod
    def _delete_by_version(cls, version_number: str):
        """
        Deletes Sequences by version number.
        """
        for scenario in _ScenarioManagerFactory()._build_manager()._repository._search("version", version_number):
            cls._delete_many(scenario.sequences.values())

    @classmethod
    def _hard_delete(cls, sequence_id: SequenceId):
        sequence = cls._get(sequence_id)
        entity_ids_to_delete = cls._get_children_entity_ids(sequence)
        entity_ids_to_delete.sequence_ids.add(sequence.id)
        cls._delete_entities_of_multiple_types(entity_ids_to_delete)

    @classmethod
    def _set(cls, sequence: Sequence):
        """
        Save or update a Sequence.
        """
        sequence_name, scenario_id = cls._breakdown_sequence_id(sequence.id)
        scenario_manager = _ScenarioManagerFactory._build_manager()

        if scenario := scenario_manager._get(scenario_id):
            sequence_data = {
                Scenario._SEQUENCE_TASKS_KEY: sequence._tasks,
                Scenario._SEQUENCE_SUBSCRIBERS_KEY: sequence._subscribers,
                Scenario._SEQUENCE_PROPERTIES_KEY: sequence._properties.data,
            }
            scenario._sequences[sequence_name] = sequence_data
            scenario_manager._set(scenario)
        else:
            cls._logger.error(f"Sequence {sequence.id} belongs to a non-existing Scenario {scenario_id}.")
            raise SequenceBelongsToNonExistingScenario(sequence.id, scenario_id)

    @classmethod
    def _create(
        cls,
        sequence_name: str,
        tasks: Union[List[Task], List[TaskId]],
        subscribers: Optional[List[_Subscriber]] = None,
        properties: Optional[Dict] = None,
        scenario_id: Optional[ScenarioId] = None,
        version: Optional[str] = None,
    ) -> Sequence:
        sequence_id = Sequence._new_id(sequence_name, scenario_id)

        task_manager = _TaskManagerFactory._build_manager()
        _tasks: List[Task] = []
        for task in tasks:
            if not isinstance(task, Task):
                if _task := task_manager._get(task):
                    _tasks.append(_task)
                else:
                    raise NonExistingTask(task)
            else:
                _tasks.append(task)

        properties = properties if properties else {}
        properties["name"] = sequence_name
        version = version if version else cls._get_latest_version()
        sequence = Sequence(
            properties=properties,
            tasks=_tasks,
            sequence_id=sequence_id,
            owner_id=scenario_id,
            parent_ids={scenario_id} if scenario_id else None,
            subscribers=subscribers,
            version=version,
        )
        for task in _tasks:
            if sequence_id not in task._parent_ids:
                task._parent_ids.update([sequence_id])
                task_manager._set(task)

        _publish_event(cls._EVENT_ENTITY_TYPE, sequence.id, EventOperation.CREATION, None)
        return sequence

    @classmethod
    def _breakdown_sequence_id(cls, sequence_id: str) -> Tuple[str, str]:
        try:
            sequence_name, scenario_id = sequence_id.split(Scenario._ID_PREFIX)
            scenario_id = f"{Scenario._ID_PREFIX}{scenario_id}"
            sequence_name = sequence_name.split(Sequence._ID_PREFIX)[1].strip("_")
            return sequence_name, scenario_id
        except (ValueError, IndexError):
            cls._logger.error(f"SequenceId {sequence_id} is invalid.")
            raise InvalidSequenceId(sequence_id)

    @classmethod
    def _get(cls, sequence: Union[str, Sequence], default=None) -> Sequence:
        """
        Returns a Sequence by id or reference.
        """
        try:
            sequence_id = sequence.id if isinstance(sequence, Sequence) else sequence
            sequence_name, scenario_id = cls._breakdown_sequence_id(sequence_id)

            scenario_manager = _ScenarioManagerFactory._build_manager()
            if scenario := scenario_manager._get(scenario_id):
                if sequence_entity := scenario.sequences.get(sequence_name, None):
                    return sequence_entity
            cls.__log_error_entity_not_found(sequence_id)
            return default
        except (ModelNotFound, InvalidSequenceId):
            cls.__log_error_entity_not_found(sequence_id)
            return default

    @classmethod
    def _get_all(cls, version_number: Optional[str] = None) -> List[Sequence]:
        """
        Returns all Sequence entities.
        """
        sequences = []
        scenarios = _ScenarioManagerFactory._build_manager()._get_all(version_number)
        for scenario in scenarios:
            sequences.extend(list(scenario.sequences.values()))

        return sequences

    @classmethod
    def _get_all_by(cls, filters: Optional[List[Dict]] = None) -> List[Sequence]:
        sequences = cls._get_all()

        if not filters:
            return sequences

        filtered_sequences = []
        for sequence in sequences:
            for filter in filters:
                if all([getattr(sequence, key) == item for key, item in filter.items()]):
                    filtered_sequences.append(sequence)
        return filtered_sequences

    @classmethod
    def _get_children_entity_ids(cls, sequence: Sequence) -> _EntityIds:
        entity_ids = _EntityIds()
        for task in sequence.tasks.values():
            if not isinstance(task, Task):
                task = _TaskManagerFactory._build_manager()._get(task)
            if task.owner_id == sequence.id:
                entity_ids.task_ids.add(task.id)
            for data_node in task.data_nodes.values():
                if data_node.owner_id == sequence.id:
                    entity_ids.data_node_ids.add(data_node.id)
        jobs = _JobManagerFactory._build_manager()._get_all()
        for job in jobs:
            if job.task.id in entity_ids.task_ids:
                entity_ids.job_ids.add(job.id)
        return entity_ids

    @classmethod
    def _subscribe(
        cls,
        callback: Callable[[Sequence, Job], None],
        params: Optional[List[Any]] = None,
        sequence: Optional[Sequence] = None,
    ):
        if sequence is None:
            sequences = cls._get_all()
            for pln in sequences:
                cls.__add_subscriber(callback, params, pln)
            return

        cls.__add_subscriber(callback, params, sequence)

    @classmethod
    def _unsubscribe(
        cls,
        callback: Callable[[Sequence, Job], None],
        params: Optional[List[Any]] = None,
        sequence: Optional[Sequence] = None,
    ):
        if sequence is None:
            sequences = cls._get_all()
            for pln in sequences:
                cls.__remove_subscriber(callback, params, pln)
            return

        cls.__remove_subscriber(callback, params, sequence)

    @classmethod
    def __add_subscriber(cls, callback, params, sequence):
        sequence._add_subscriber(callback, params)
        _publish_event(cls._EVENT_ENTITY_TYPE, sequence.id, EventOperation.UPDATE, "subscribers")

    @classmethod
    def __remove_subscriber(cls, callback, params, sequence):
        sequence._remove_subscriber(callback, params)
        _publish_event(cls._EVENT_ENTITY_TYPE, sequence.id, EventOperation.UPDATE, "subscribers")

    @classmethod
    def _is_submittable(cls, sequence: Union[Sequence, SequenceId]) -> bool:
        if isinstance(sequence, str):
            sequence = cls._get(sequence)
        return isinstance(sequence, Sequence)

    @classmethod
    def _submit(
        cls,
        sequence: Union[SequenceId, Sequence],
        callbacks: Optional[List[Callable]] = None,
        force: bool = False,
        wait: bool = False,
        timeout: Optional[Union[float, int]] = None,
        check_inputs_are_ready: bool = True,
    ) -> List[Job]:
        sequence_id = sequence.id if isinstance(sequence, Sequence) else sequence
        sequence = cls._get(sequence_id)
        if sequence is None:
            raise NonExistingSequence(sequence_id)
        callbacks = callbacks or []
        sequence_subscription_callback = cls.__get_status_notifier_callbacks(sequence) + callbacks
        if check_inputs_are_ready:
            _warn_if_inputs_not_ready(sequence.get_inputs())

        jobs = (
            _TaskManagerFactory._build_manager()
            ._orchestrator()
            .submit(sequence, callbacks=sequence_subscription_callback, force=force, wait=wait, timeout=timeout)
        )
        _publish_event(cls._EVENT_ENTITY_TYPE, sequence.id, EventOperation.SUBMISSION, None)
        return jobs

    @classmethod
    def _exists(cls, entity_id: str) -> bool:
        """
        Returns True if the entity id exists.
        """
        return True if cls._get(entity_id) else False

    @classmethod
    def _export(cls, id: str, folder_path: Union[str, pathlib.Path]):
        """
        Export a Sequence entity.
        """
        if isinstance(folder_path, str):
            folder: pathlib.Path = pathlib.Path(folder_path)
        else:
            folder = folder_path

        export_dir = folder / cls._model_name
        if not export_dir.exists():
            export_dir.mkdir(parents=True)

        export_path = export_dir / f"{id}.json"
        sequence_name, scenario_id = cls._breakdown_sequence_id(id)
        sequence = {"id": id, "owner_id": scenario_id, "parent_ids": [scenario_id], "name": sequence_name}

        scenario = _ScenarioManagerFactory._build_manager()._get(scenario_id)
        if sequence_data := scenario._sequences.get(sequence_name, None):
            sequence.update(sequence_data)
            with open(export_path, "w", encoding="utf-8") as export_file:
                export_file.write(json.dumps(sequence))
        else:
            raise ModelNotFound(cls._model_name, id)

    @classmethod
    def __log_error_entity_not_found(cls, sequence_id: Union[SequenceId, str]):
        cls._logger.error(f"{cls._ENTITY_NAME} not found: {str(sequence_id)}")

    @staticmethod
    def __get_status_notifier_callbacks(sequence: Sequence) -> List:
        return [partial(c.callback, *c.params, sequence) for c in sequence.subscribers]
