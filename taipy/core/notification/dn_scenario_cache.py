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
from typing import TYPE_CHECKING, Dict, List

if TYPE_CHECKING:
    from .._entity.submittable import Submittable
    from ..data.data_node import DataNode, DataNodeId


class SubmittableStatusCache:
    datanode_id_submittables: Dict["DataNodeId", List["Submittable"]] = defaultdict(lambda: [])
    submittable_id_datanodes: Dict[str, List["DataNode"]] = defaultdict(lambda: [])

    @classmethod
    def add(cls, entity: "Submittable", datanode: "DataNode"):
        cls.datanode_id_submittables[datanode.id].append(entity)
        cls.submittable_id_datanodes[entity.id].append(datanode)  # type: ignore

    @classmethod
    def remove(cls, datanode: "DataNode"):
        submittables = cls.datanode_id_submittables.pop(datanode.id, [])
        for submittable in submittables:
            cls.submittable_id_datanodes[submittable.id].remove(datanode)
            if len(cls.submittable_id_datanodes[submittable.id]) == 0:
                # Notifier.publish(make_event(scenario, submittable, UPDATE))
                cls.submittable_id_datanodes.pop(submittable.id)
