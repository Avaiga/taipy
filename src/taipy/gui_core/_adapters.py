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

import typing as t
from enum import Enum

from taipy.core import Cycle, DataNode, Job, Scenario, Sequence
from taipy.core import get as core_get
from taipy.core import is_deletable, is_promotable, is_submittable
from taipy.gui.gui import _DoNotUpdate
from taipy.gui.utils import _TaipyBase


# prevent gui from trying to push scenario instances to the front-end
class _GCDoNotUpdate(_DoNotUpdate):
    def __repr__(self):
        return self.get_label() if hasattr(self, "get_label") else super().__repr__()


Scenario.__bases__ += (_GCDoNotUpdate,)
Sequence.__bases__ += (_GCDoNotUpdate,)
DataNode.__bases__ += (_GCDoNotUpdate,)
Job.__bases__ += (_GCDoNotUpdate,)


class _EntityType(Enum):
    CYCLE = 0
    SCENARIO = 1
    SEQUENCE = 2
    DATANODE = 3


class _GuiCoreScenarioAdapter(_TaipyBase):
    __INNER_PROPS = ["name"]

    def get(self):
        data = super().get()
        if isinstance(data, Scenario):
            scenario = core_get(data.id)
            if scenario:
                return [
                    scenario.id,
                    scenario.is_primary,
                    scenario.config_id,
                    scenario.cycle.get_simple_label() if scenario.cycle else "",
                    scenario.get_simple_label(),
                    list(scenario.tags) if scenario.tags else [],
                    [(k, v) for k, v in scenario.properties.items() if k not in _GuiCoreScenarioAdapter.__INNER_PROPS]
                    if scenario.properties
                    else [],
                    [(p.id, p.get_simple_label(), is_submittable(p)) for p in scenario.sequences.values()]
                    if scenario.sequences
                    else [],
                    list(scenario.properties.get("authorized_tags", [])) if scenario.properties else [],
                    is_deletable(scenario),
                    is_promotable(scenario),
                    is_submittable(scenario),
                ]
        return None

    @staticmethod
    def get_hash():
        return _TaipyBase._HOLDER_PREFIX + "Sc"


class _GuiCoreScenarioDagAdapter(_TaipyBase):
    @staticmethod
    def get_entity_type(node: t.Any):
        return DataNode.__name__ if isinstance(node.entity, DataNode) else node.type

    def get(self):
        data = super().get()
        if isinstance(data, Scenario):
            scenario = core_get(data.id)
            if scenario:
                dag = data._get_dag()
                nodes = dict()
                for id, node in dag.nodes.items():
                    entityType = _GuiCoreScenarioDagAdapter.get_entity_type(node)
                    cat = nodes.get(entityType)
                    if cat is None:
                        cat = dict()
                        nodes[entityType] = cat
                    cat[id] = {
                        "name": node.entity.get_simple_label(),
                        "type": node.entity.storage_type() if hasattr(node.entity, "storage_type") else None,
                    }
                return [
                    data.id,
                    nodes,
                    [
                        (
                            _GuiCoreScenarioDagAdapter.get_entity_type(e.src),
                            e.src.entity.id,
                            _GuiCoreScenarioDagAdapter.get_entity_type(e.dest),
                            e.dest.entity.id,
                        )
                        for e in dag.edges
                    ],
                ]
        return None

    @staticmethod
    def get_hash():
        return _TaipyBase._HOLDER_PREFIX + "ScG"


class _GuiCoreDatanodeAdapter(_TaipyBase):
    __INNER_PROPS = ["name"]

    def get(self):
        data = super().get()
        if isinstance(data, DataNode):
            datanode = core_get(data.id)
            if datanode:
                owner = core_get(datanode.owner_id) if datanode.owner_id else None
                return [
                    datanode.id,
                    datanode.storage_type() if hasattr(datanode, "storage_type") else "",
                    datanode.config_id,
                    f"{datanode.last_edit_date}" if datanode.last_edit_date else "",
                    f"{datanode.expiration_date}" if datanode.last_edit_date else "",
                    datanode.get_simple_label(),
                    datanode.owner_id or "",
                    owner.get_simple_label() if owner else "GLOBAL",
                    _EntityType.CYCLE.value
                    if isinstance(owner, Cycle)
                    else _EntityType.SCENARIO.value
                    if isinstance(owner, Scenario)
                    else -1,
                    [
                        (k, f"{v}")
                        for k, v in datanode._get_user_properties().items()
                        if k not in _GuiCoreDatanodeAdapter.__INNER_PROPS
                    ],
                    datanode._edit_in_progress,
                    datanode._editor_id,
                ]
        return None

    @staticmethod
    def get_hash():
        return _TaipyBase._HOLDER_PREFIX + "Dn"
