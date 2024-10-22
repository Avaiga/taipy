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

from typing import Callable, List, Optional, Type, Union, cast

from taipy.common.config import Config
from taipy.common.config.common.scope import Scope

from .._entity._entity_ids import _EntityIds
from .._manager._manager import _Manager
from .._orchestrator._abstract_orchestrator import _AbstractOrchestrator
from .._repository._abstract_repository import _AbstractRepository
from .._version._version_manager_factory import _VersionManagerFactory
from .._version._version_mixin import _VersionMixin
from ..common.warn_if_inputs_not_ready import _warn_if_inputs_not_ready
from ..config.task_config import TaskConfig
from ..cycle.cycle_id import CycleId
from ..data._data_manager_factory import _DataManagerFactory
from ..exceptions.exceptions import NonExistingTask
from ..notification import EventEntityType, EventOperation, Notifier, _make_event
from ..reason import (
    DataNodeEditInProgress,
    DataNodeIsNotWritten,
    EntityDoesNotExist,
    EntityIsNotSubmittableEntity,
    ReasonCollection,
)
from ..scenario.scenario_id import ScenarioId
from ..sequence.sequence_id import SequenceId
from ..submission.submission import Submission
from ..task.task import Task
from .task_id import TaskId


class _TaskManager(_Manager[Task], _VersionMixin):
    _ENTITY_NAME = Task.__name__
    _repository: _AbstractRepository
    _EVENT_ENTITY_TYPE = EventEntityType.TASK

    @classmethod
    def _orchestrator(cls) -> Type[_AbstractOrchestrator]:
        from .._orchestrator._orchestrator_factory import _OrchestratorFactory

        return _OrchestratorFactory._build_orchestrator()

    @classmethod
    def _set(cls, task: Task) -> None:
        cls.__save_data_nodes(task.input.values())
        cls.__save_data_nodes(task.output.values())
        super()._set(task)

    @classmethod
    def _bulk_get_or_create(
        cls,
        task_configs: List[TaskConfig],
        cycle_id: Optional[CycleId] = None,
        scenario_id: Optional[ScenarioId] = None,
    ) -> List[Task]:
        data_node_configs = set()
        for task_config in task_configs:
            data_node_configs.update([Config.data_nodes[dnc.id] for dnc in task_config.input_configs])
            data_node_configs.update([Config.data_nodes[dnc.id] for dnc in task_config.output_configs])

        data_nodes = _DataManagerFactory._build_manager()._bulk_get_or_create(
            list(data_node_configs), cycle_id, scenario_id
        )
        tasks_configs_and_owner_id = []
        for task_config in task_configs:
            task_dn_configs = [Config.data_nodes[dnc.id] for dnc in task_config.output_configs] + [
                Config.data_nodes[dnc.id] for dnc in task_config.input_configs
            ]
            task_config_data_nodes = [data_nodes[dn_config] for dn_config in task_dn_configs]
            scope = min(dn.scope for dn in task_config_data_nodes) if len(task_config_data_nodes) != 0 else Scope.GLOBAL
            owner_id: Union[Optional[SequenceId], Optional[ScenarioId], Optional[CycleId]]
            if scope == Scope.SCENARIO:
                owner_id = scenario_id
            elif scope == Scope.CYCLE:
                owner_id = cycle_id
            else:
                owner_id = None

            tasks_configs_and_owner_id.append((task_config, owner_id))

        tasks_by_config = cls._repository._get_by_configs_and_owner_ids(  # type: ignore
            tasks_configs_and_owner_id, cls._build_filters_with_version(None)
        )

        tasks = []
        for task_config, owner_id in tasks_configs_and_owner_id:
            if task := tasks_by_config.get((task_config, owner_id)):
                tasks.append(task)
            else:
                version = _VersionManagerFactory._build_manager()._get_latest_version()
                inputs = [
                    data_nodes[input_config]
                    for input_config in [Config.data_nodes[dnc.id] for dnc in task_config.input_configs]
                ]
                outputs = [
                    data_nodes[output_config]
                    for output_config in [Config.data_nodes[dnc.id] for dnc in task_config.output_configs]
                ]
                skippable = task_config.skippable

                task = Task(
                    str(task_config.id),
                    dict(**task_config._properties),
                    cast(Callable, task_config.function),
                    inputs,
                    outputs,
                    owner_id=owner_id,
                    parent_ids=set(),
                    version=version,
                    skippable=skippable,
                )
                for dn in set(inputs + outputs):
                    dn._parent_ids.update([task.id])
                cls._set(task)
                Notifier.publish(_make_event(task, EventOperation.CREATION))
                tasks.append(task)
        return tasks

    @classmethod
    def _get_all(cls, version_number: Optional[str] = None) -> List[Task]:
        """
        Returns all entities.
        """
        filters = cls._build_filters_with_version(version_number)
        return cls._repository._load_all(filters)

    @classmethod
    def __save_data_nodes(cls, data_nodes) -> None:
        data_manager = _DataManagerFactory._build_manager()
        for i in data_nodes:
            data_manager._set(i)

    @classmethod
    def _hard_delete(cls, task_id: TaskId) -> None:
        task = cls._get(task_id)
        entity_ids_to_delete = cls._get_children_entity_ids(task)
        entity_ids_to_delete.task_ids.add(task.id)
        cls._delete_entities_of_multiple_types(entity_ids_to_delete)

    @classmethod
    def _get_children_entity_ids(cls, task: Task) -> _EntityIds:
        entity_ids = _EntityIds()

        from ..job._job_manager_factory import _JobManagerFactory
        from ..submission._submission_manager_factory import _SubmissionManagerFactory

        jobs = _JobManagerFactory._build_manager()._get_all()

        for job in jobs:
            if job.task.id == task.id:
                entity_ids.job_ids.add(job.id)

        submissions = _SubmissionManagerFactory._build_manager()._get_all()
        submitted_entity_ids = list(entity_ids.task_ids)
        for submission in submissions:
            if submission.entity_id in submitted_entity_ids:
                entity_ids.submission_ids.add(submission.id)

        return entity_ids

    @classmethod
    def _is_submittable(cls, task: Union[Task, TaskId]) -> ReasonCollection:
        reason_collection = ReasonCollection()

        if isinstance(task, str):
            task_id = task
            task = cls._get(task)
            if task is None:
                reason_collection._add_reason(task_id, EntityDoesNotExist(task_id))

        if not isinstance(task, Task):
            reason_collection._add_reason(str(task), EntityIsNotSubmittableEntity(str(task)))
        else:
            data_manager = _DataManagerFactory._build_manager()
            for node in task.input.values():
                node = data_manager._get(node)
                if node._edit_in_progress:
                    reason_collection._add_reason(node.id, DataNodeEditInProgress(node.id))
                if not node._last_edit_date:
                    reason_collection._add_reason(node.id, DataNodeIsNotWritten(node.id))

        return reason_collection

    @classmethod
    def _submit(
        cls,
        task: Union[TaskId, Task],
        callbacks: Optional[List[Callable]] = None,
        force: bool = False,
        wait: bool = False,
        timeout: Optional[Union[float, int]] = None,
        check_inputs_are_ready: bool = True,
        **properties,
    ) -> Submission:
        task_id = task.id if isinstance(task, Task) else task
        task = cls._get(task_id)
        if task is None:
            raise NonExistingTask(task_id)
        if check_inputs_are_ready:
            _warn_if_inputs_not_ready(task.input.values())
        submission = cls._orchestrator().submit_task(
            task, callbacks=callbacks, force=force, wait=wait, timeout=timeout, **properties
        )
        Notifier.publish(_make_event(task, EventOperation.SUBMISSION))
        return submission

    @classmethod
    def _get_by_config_id(cls, config_id: str, version_number: Optional[str] = None) -> List[Task]:
        """
        Get all tasks by its config id.
        """
        filters = cls._build_filters_with_version(version_number)
        if not filters:
            filters = [{}]
        for fil in filters:
            fil.update({"config_id": config_id})
        return cls._repository._load_all(filters)
