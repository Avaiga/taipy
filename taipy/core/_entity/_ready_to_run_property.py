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

from collections import defaultdict
from typing import TYPE_CHECKING, Dict, Set, Union

from ..notification import EventOperation, Notifier, _make_event

if TYPE_CHECKING:
    from ..data.data_node import DataNode, DataNodeId
    from ..scenario.scenario import ScenarioId
    from ..sequence.sequence import SequenceId
    from ..task.task import TaskId


class _ReadyToRunProperty:
    IS_SUBMITTABLE_PROPERTY_NAME: str = "is_submittable"

    # A dictionary of the data nodes not ready_to_read and their corresponding submittable entities.
    _datanode_id_submittables: Dict["DataNodeId", Set[Union["ScenarioId", "SequenceId", "TaskId"]]] = defaultdict(set)

    # A nested dictionary of the submittable entities (Scenario, Sequence, Task) and
    # the data nodes that make it not ready_to_run with the reason(s)
    _submittable_id_datanodes: Dict[
        Union["ScenarioId", "SequenceId", "TaskId"], Dict["DataNodeId", Set[str]]
    ] = defaultdict(lambda: defaultdict(set))

    @staticmethod
    def _publish_submittable_property_event(
        submittable_id: Union["ScenarioId", "SequenceId", "TaskId"], submittable_property
    ):
        from ..taipy import get as tp_get

        Notifier.publish(
            _make_event(
                tp_get(submittable_id),
                EventOperation.UPDATE,
                attribute_name=_ReadyToRunProperty.IS_SUBMITTABLE_PROPERTY_NAME,
                attribute_value=submittable_property,
            )
        )

    @classmethod
    def __add_unsubmittable_reason(
        cls, submittable_id: Union["ScenarioId", "SequenceId", "TaskId"], datanode_id: "DataNodeId", reason: str
    ):
        cls._datanode_id_submittables[datanode_id].add(submittable_id)
        if submittable_id not in cls._submittable_id_datanodes:
            cls._publish_submittable_property_event(submittable_id, False)
        cls._submittable_id_datanodes[submittable_id][datanode_id].add(reason)

    @classmethod
    def _remove(cls, datanode_id: "DataNodeId", reason: str):
        # check the data node status to determine the reason to be removed
        submittable_ids: Set = cls._datanode_id_submittables.get(datanode_id, set())

        to_remove_dn = False
        for submittable_id in submittable_ids:
            # check remove the reason
            if reason in cls._submittable_id_datanodes[submittable_id].get(datanode_id, set()):
                cls._submittable_id_datanodes[submittable_id].get(datanode_id, set()).remove(reason)
            if len(cls._submittable_id_datanodes[submittable_id][datanode_id]) == 0:
                to_remove_dn = True
                cls._submittable_id_datanodes[submittable_id].pop(datanode_id, None)
                if len(cls._submittable_id_datanodes[submittable_id]) == 0:
                    cls._publish_submittable_property_event(submittable_id, True)
                    cls._submittable_id_datanodes.pop(submittable_id, None)

        if to_remove_dn:
            cls._datanode_id_submittables.pop(datanode_id)

    @classmethod
    def _check_submittable_is_ready_to_submit(cls, submittable_id: Union["ScenarioId", "SequenceId", "TaskId"]):
        return len(_ReadyToRunProperty._submittable_id_datanodes.get(submittable_id, [])) == 0

    @classmethod
    def _add_parent_entities_to_submittable_cache(cls, dn: "DataNode", reason: str):
        from ..scenario.scenario import Scenario
        from ..sequence.sequence import Sequence
        from ..task.task import Task

        parent_entities = dn.get_parents()

        for scenario_parent in parent_entities.get(Scenario._MANAGER_NAME, []):
            _ReadyToRunProperty.__add_unsubmittable_reason(scenario_parent.id, dn.id, reason)
        for sequence_parent in parent_entities.get(Sequence._MANAGER_NAME, []):
            _ReadyToRunProperty.__add_unsubmittable_reason(sequence_parent.id, dn.id, reason)
        for task_parent in parent_entities.get(Task._MANAGER_NAME, []):
            _ReadyToRunProperty.__add_unsubmittable_reason(task_parent.id, dn.id, reason)
