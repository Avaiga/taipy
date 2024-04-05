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
    datanode_id_submittables: Dict["DataNodeId", Set[str]] = defaultdict(lambda: set())
    submittable_id_datanodes: Dict[str, Set["DataNodeId"]] = defaultdict(lambda: set())

    @classmethod
    def add(cls, entity_id: str, datanode_id: "DataNodeId"):
        cls.datanode_id_submittables[datanode_id].add(entity_id)
        cls.submittable_id_datanodes[entity_id].add(datanode_id)  # type: ignore

    @classmethod
    def remove(cls, datanode_id: "DataNode"):
        submittable_ids: Set = cls.datanode_id_submittables.pop(datanode_id, set())
        for submittable_id in submittable_ids:
            cls.submittable_id_datanodes[submittable_id].remove(datanode_id)
            if len(cls.submittable_id_datanodes[submittable_id]) == 0:
                # Notifier.publish(make_event(scenario, submittable, UPDATE))
                cls.submittable_id_datanodes.pop(submittable_id)
