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
from typing import TYPE_CHECKING, Dict, Set

if TYPE_CHECKING:
    from ..data.data_node import DataNode, DataNodeId


class SubmittableStatusCache:
    # A dictionary representing not ready_to_read datanode and its equivalent submittable entities
    datanode_id_submittables: Dict["DataNodeId", Set[str]] = defaultdict(lambda: set())

    # A nested dictionary representing the submittable entities (Scenario, Sequence, Task) and
    # its equivalent not ready_to_read input datanodes
    submittable_id_datanodes: Dict[str, Dict["DataNodeId", str]] = defaultdict(defaultdict)

    @classmethod
    def __add(cls, entity_id: str, datanode_id: "DataNodeId", reason: str):
        cls.datanode_id_submittables[datanode_id].add(entity_id)
        cls.submittable_id_datanodes[entity_id][datanode_id] = reason

    @classmethod
    def __remove(cls, datanode_id: "DataNodeId"):
        submittable_ids: Set = cls.datanode_id_submittables.pop(datanode_id, set())
        for submittable_id in submittable_ids:
            cls.submittable_id_datanodes[submittable_id].pop(datanode_id, None)
            if len(cls.submittable_id_datanodes[submittable_id]) == 0:
                # Notifier.publish(make_event(scenario, submittable, UPDATE))
                cls.submittable_id_datanodes.pop(submittable_id, None)

    @classmethod
    def _check_submittable_is_ready_to_submit(cls, entity_id: str):
        return len(SubmittableStatusCache.submittable_id_datanodes.get(entity_id, [])) == 0

    @classmethod
    def __add_parent_entities_to_submittable_cache(cls, dn: "DataNode", reason: str):
        from ..scenario.scenario import Scenario
        from ..sequence.sequence import Sequence
        from ..task.task import Task

        parent_entities = dn.get_parents()

        for scenario_parent in parent_entities.get(Scenario._MANAGER_NAME, []):
            SubmittableStatusCache.__add(scenario_parent.id, dn.id, reason)
        for sequence_parent in parent_entities.get(Sequence._MANAGER_NAME, []):
            SubmittableStatusCache.__add(sequence_parent.id, dn.id, reason)
        for task_parent in parent_entities.get(Task._MANAGER_NAME, []):
            SubmittableStatusCache.__add(task_parent.id, dn.id, reason)

    @classmethod
    def _compute_if_dn_is_ready_for_reading(cls, dn: "DataNode"):
        if dn._edit_in_progress:
            cls.__add_parent_entities_to_submittable_cache(dn, f"DataNode {dn.id} is being edited.")
        elif not dn._last_edit_date:
            cls.__add_parent_entities_to_submittable_cache(dn, f"DataNode {dn.id} is not written.")
        elif dn.is_ready_for_reading:
            SubmittableStatusCache.__remove(dn.id)
