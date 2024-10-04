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

from typing import TYPE_CHECKING, Dict, Set, Union

from ..notification import EventOperation, Notifier, _make_event
from ..reason import Reason, ReasonCollection

if TYPE_CHECKING:
    from ..data.data_node import DataNode, DataNodeId
    from ..scenario.scenario import Scenario, ScenarioId
    from ..sequence.sequence import Sequence, SequenceId
    from ..task.task import Task, TaskId


class _ReadyToRunProperty:
    IS_SUBMITTABLE_PROPERTY_NAME: str = "is_submittable"

    # A dictionary of the data nodes not ready_to_read and their corresponding submittable entities.
    _datanode_id_submittables: Dict["DataNodeId", Set[Union["ScenarioId", "SequenceId", "TaskId"]]] = {}

    # A nested dictionary of the submittable entities (Scenario, Sequence, Task) and
    # the data nodes that make it not ready_to_run with the reason(s)
    _submittable_id_datanodes: Dict[Union["ScenarioId", "SequenceId", "TaskId"], ReasonCollection] = {}

    @classmethod
    def _add(cls, dn: "DataNode", reason: Reason) -> None:
        from ..scenario.scenario import Scenario
        from ..sequence.sequence import Sequence
        from ..task.task import Task

        parent_entities = dn.get_parents()

        for scenario_parent in parent_entities.get(Scenario._MANAGER_NAME, []):
            if dn in scenario_parent.get_inputs():
                cls.__add(scenario_parent, dn, reason)  # type: ignore
        for sequence_parent in parent_entities.get(Sequence._MANAGER_NAME, []):
            if dn in sequence_parent.get_inputs():
                cls.__add(sequence_parent, dn, reason)  # type: ignore
        for task_parent in parent_entities.get(Task._MANAGER_NAME, []):
            if dn in task_parent.input.values():
                cls.__add(task_parent, dn, reason)  # type: ignore

    @classmethod
    def _remove(cls, datanode: "DataNode", reason: Reason) -> None:
        from ..taipy import get as tp_get

        # check the data node status to determine the reason to be removed
        submittable_ids: Set = cls._datanode_id_submittables.get(datanode.id, set())

        to_remove_dn = False
        for submittable_id in submittable_ids:
            # check remove the reason
            reason_entity = cls._submittable_id_datanodes.get(submittable_id)
            if reason_entity is not None:
                reason_entity._remove_reason(datanode.id, reason)
                to_remove_dn = not reason_entity._entity_id_exists_in_reason(datanode.id)
                if reason_entity:
                    submittable = tp_get(submittable_id)
                    cls.__publish_submittable_property_event(submittable, True)
                    cls._submittable_id_datanodes.pop(submittable_id)

        if to_remove_dn:
            cls._datanode_id_submittables.pop(datanode.id)

    @classmethod
    def __add(cls, submittable: Union["Scenario", "Sequence", "Task"], datanode: "DataNode", reason: Reason) -> None:
        if datanode.id not in cls._datanode_id_submittables:
            cls._datanode_id_submittables[datanode.id] = set()
        cls._datanode_id_submittables[datanode.id].add(submittable.id)

        if submittable.id not in cls._submittable_id_datanodes:
            cls.__publish_submittable_property_event(submittable, False)

        if submittable.id not in cls._submittable_id_datanodes:
            cls._submittable_id_datanodes[submittable.id] = ReasonCollection()
        cls._submittable_id_datanodes[submittable.id]._add_reason(datanode.id, reason)

    @staticmethod
    def __publish_submittable_property_event(
        submittable: Union["Scenario", "Sequence", "Task"], submittable_property
    ) -> None:
        Notifier.publish(
            _make_event(
                submittable,
                EventOperation.UPDATE,
                attribute_name=_ReadyToRunProperty.IS_SUBMITTABLE_PROPERTY_NAME,
                attribute_value=submittable_property,
            )
        )
