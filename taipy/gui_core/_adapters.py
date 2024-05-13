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

import inspect
import json
import math
import typing as t
from enum import Enum
from numbers import Number
from operator import attrgetter, contains, eq, ge, gt, le, lt, ne

import pandas as pd

from taipy.core import (
    Cycle,
    DataNode,
    Job,
    Scenario,
    Sequence,
    Task,
    is_deletable,
    is_editable,
    is_promotable,
    is_readable,
    is_submittable,
)
from taipy.core import get as core_get
from taipy.core.data._tabular_datanode_mixin import _TabularDataNodeMixin
from taipy.gui._warnings import _warn
from taipy.gui.gui import _DoNotUpdate
from taipy.gui.utils import _TaipyBase


# prevent gui from trying to push scenario instances to the front-end
class _GCDoNotUpdate(_DoNotUpdate):
    def __repr__(self):
        return self.get_label() if hasattr(self, "get_label") else super().__repr__()


Scenario.__bases__ += (_GCDoNotUpdate,)
Sequence.__bases__ += (_GCDoNotUpdate,)
DataNode.__bases__ += (_GCDoNotUpdate,)
Cycle.__bases__ += (_GCDoNotUpdate,)
Job.__bases__ += (_GCDoNotUpdate,)
Task.__bases__ += (_GCDoNotUpdate,)


class _EntityType(Enum):
    CYCLE = 0
    SCENARIO = 1
    SEQUENCE = 2
    DATANODE = 3


class _GuiCoreScenarioAdapter(_TaipyBase):
    __INNER_PROPS = ["name"]

    def get(self):
        data = super().get()
        if isinstance(data, (list, tuple)) and len(data) == 1:
            data = data[0]
        if isinstance(data, Scenario):
            try:
                if scenario := core_get(data.id):
                    return [
                        scenario.id,
                        scenario.is_primary,
                        scenario.config_id,
                        scenario.creation_date.isoformat(),
                        scenario.cycle.get_simple_label() if scenario.cycle else "",
                        scenario.get_simple_label(),
                        list(scenario.tags) if scenario.tags else [],
                        [
                            (k, v)
                            for k, v in scenario.properties.items()
                            if k not in _GuiCoreScenarioAdapter.__INNER_PROPS
                        ]
                        if scenario.properties
                        else [],
                        [
                            (
                                s.get_simple_label(),
                                [t.id for t in s.tasks.values()] if hasattr(s, "tasks") else [],
                                is_submittable(s),
                                is_editable(s),
                            )
                            for s in scenario.sequences.values()
                        ]
                        if hasattr(scenario, "sequences") and scenario.sequences
                        else [],
                        {t.id: t.get_simple_label() for t in scenario.tasks.values()}
                        if hasattr(scenario, "tasks")
                        else {},
                        list(scenario.properties.get("authorized_tags", [])) if scenario.properties else [],
                        is_deletable(scenario),
                        is_promotable(scenario),
                        is_submittable(scenario),
                        is_readable(scenario),
                        is_editable(scenario),
                    ]
            except Exception as e:
                _warn(f"Access to scenario ({data.id if hasattr(data, 'id') else 'No_id'}) failed", e)

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
        if isinstance(data, (list, tuple)) and len(data) == 1:
            data = data[0]
        if isinstance(data, Scenario):
            try:
                if scenario := core_get(data.id):
                    dag = scenario._get_dag()
                    nodes = {}
                    for id, node in dag.nodes.items():
                        entityType = _GuiCoreScenarioDagAdapter.get_entity_type(node)
                        cat = nodes.get(entityType)
                        if cat is None:
                            cat = {}
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
            except Exception as e:
                _warn(f"Access to scenario ({data.id if hasattr(data, 'id') else 'No_id'}) failed", e)

        return None

    @staticmethod
    def get_hash():
        return _TaipyBase._HOLDER_PREFIX + "ScG"


class _GuiCoreScenarioNoUpdate(_TaipyBase, _DoNotUpdate):
    @staticmethod
    def get_hash():
        return _TaipyBase._HOLDER_PREFIX + "ScN"


class _GuiCoreDatanodeAdapter(_TaipyBase):
    @staticmethod
    def _is_tabular_data(datanode: DataNode, value: t.Any):
        return isinstance(datanode, _TabularDataNodeMixin) or isinstance(
            value, (pd.DataFrame, pd.Series, list, tuple, dict)
        )

    def __get_data(self, dn: DataNode):
        if dn._last_edit_date:
            if isinstance(dn, _TabularDataNodeMixin):
                return (None, None, True, None)
            try:
                value = dn.read()
                if _GuiCoreDatanodeAdapter._is_tabular_data(dn, value):
                    return (None, None, True, None)
                val_type = (
                    "date"
                    if "date" in type(value).__name__
                    else type(value).__name__
                    if isinstance(value, Number)
                    else None
                )
                if isinstance(value, float) and math.isnan(value):
                    value = None
                return (
                    value,
                    val_type,
                    None,
                    None,
                )
            except Exception as e:
                return (None, None, None, f"read data_node: {e}")
        return (None, None, None, f"Data unavailable for {dn.get_simple_label()}")

    def get(self):
        data = super().get()
        if isinstance(data, (list, tuple)) and len(data) == 1:
            data = data[0]
        if isinstance(data, DataNode):
            try:
                if datanode := core_get(data.id):
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
                        self.__get_data(datanode),
                        datanode._edit_in_progress,
                        datanode._editor_id,
                        is_readable(datanode),
                        is_editable(datanode),
                    ]
            except Exception as e:
                _warn(f"Access to datanode ({data.id if hasattr(data, 'id') else 'No_id'}) failed", e)

        return None

    @staticmethod
    def get_hash():
        return _TaipyBase._HOLDER_PREFIX + "Dn"


def _attr_filter(attrVal: t.Any):
    return not inspect.isroutine(attrVal)


def _attr_type(attr: str):
    return "date" if "date" in attr else "boolean" if attr.startswith("is_") else "string"


_operators: t.Dict[str, t.Callable] = {
    "==": eq,
    "!=": ne,
    "<": lt,
    "<=": le,
    ">": gt,
    ">=": ge,
    "contains": contains,
}


def _invoke_action(ent: t.Any, col: str, action: str, val: t.Any) -> bool:
    try:
        if op := _operators.get(action):
            return op(attrgetter(col)(ent), val)
    except Exception as e:
        _warn(f"Error filtering with {col} {action} {val} on {ent}.", e)
    return True


class _GuiCoreScenarioProperties(_TaipyBase):
    __SCENARIO_ATTRIBUTES = [a[0] for a in inspect.getmembers(Scenario, _attr_filter) if not a[0].startswith("_")]
    __DATANODE_ATTRIBUTES = [a[0] for a in inspect.getmembers(DataNode, _attr_filter) if not a[0].startswith("_")]

    @staticmethod
    def get_hash():
        return _TaipyBase._HOLDER_PREFIX + "ScP"

    def get(self):
        data = super().get()
        if isinstance(data, str):
            data = data.split(";")
        if isinstance(data, (list, tuple)):
            return json.dumps(
                [
                    (attr, _attr_type(attr))
                    for attr in data
                    if attr
                    and isinstance(attr, str)
                    and (parts := attr.split("."))
                    and (len(parts) > 1 and parts[1] in _GuiCoreScenarioProperties.__DATANODE_ATTRIBUTES)
                    or attr in _GuiCoreScenarioProperties.__SCENARIO_ATTRIBUTES
                ]
            )
        return None
