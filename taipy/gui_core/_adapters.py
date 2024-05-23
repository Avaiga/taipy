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

import json
import math
import typing as t
from datetime import date, datetime
from enum import Enum
from numbers import Number
from operator import attrgetter, contains, eq, ge, gt, le, lt, ne

import pandas as pd

from taipy.core import (
    Cycle,
    DataNode,
    Scenario,
    is_deletable,
    is_editable,
    is_promotable,
    is_readable,
    is_submittable,
)
from taipy.core import get as core_get
from taipy.core.config import Config
from taipy.core.data._tabular_datanode_mixin import _TabularDataNodeMixin
from taipy.gui._warnings import _warn
from taipy.gui.gui import _DoNotUpdate
from taipy.gui.utils import _is_boolean, _is_boolean_true, _TaipyBase


# prevent gui from trying to push scenario instances to the front-end
class _GCDoNotUpdate(_DoNotUpdate):
    def __repr__(self):
        return self.get_label() if hasattr(self, "get_label") else super().__repr__()


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
                                True if (reason := is_submittable(s)) else reason.reasons,
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
                        True if (reason := is_submittable(scenario)) else reason.reasons,
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


_operators: t.Dict[str, t.Callable] = {
    "==": eq,
    "!=": ne,
    "<": lt,
    "<=": le,
    ">": gt,
    ">=": ge,
    "contains": contains,
}


def _invoke_action(ent: t.Any, col: str, col_type: str, is_dn: bool, action: str, val: t.Any) -> bool:
    try:
        if col_type == "any":
            # when a property is not found, return True only if action is not equals
            entity = getattr(ent, col.split(".")[0]) if is_dn else ent
            if not hasattr(entity, "properties") or not entity.properties.get(col):
                return action == "!="
        if op := _operators.get(action):
            cur_val = attrgetter(col)(ent)
            return op(cur_val.isoformat() if isinstance(cur_val, (datetime, date)) else cur_val, val)
    except Exception as e:
        _warn(f"Error filtering with {col} {action} {val} on {ent}.", e)
    return True


def _get_datanode_property(attr: str):
    if (parts := attr.split(".")) and len(parts) > 1:
        return parts[1]
    return None


class _GuiCoreScenarioProperties(_TaipyBase):
    __SC_TYPES = {
        "config id": "string",
        "label": "string",
        "creation date": "date",
        "cycle label": "string",
        "cycle start": "date",
        "cycle end": "date",
        "primary": "boolean",
        "tags": "string",
    }
    __SC_NAMES = {
        "config id": "config_id",
        "creation date": "creation_date",
        "label": "name",
        "cycle label": "cycle.name",
        "cycle start": "cycle.start",
        "cycle end": "cycle.end",
        "primary": "is_primary",
    }
    DEFAULT = list(__SC_TYPES.keys())
    __DN_TYPES = {"up to date": "boolean", "valid": "boolean", "last edit date": "date"}
    __DN_NAMES = {"up to date": "is_up_to_date", "is_valid": "valid", "last edit date": "last_edit_date"}
    __ENUMS = None

    @staticmethod
    def get_hash():
        return _TaipyBase._HOLDER_PREFIX + "ScP"

    @staticmethod
    def get_type(attr: str):
        if prop := _get_datanode_property(attr):
            return _GuiCoreScenarioProperties.__DN_TYPES.get(prop, "any")
        return _GuiCoreScenarioProperties.__SC_TYPES.get(attr, "any")

    @staticmethod
    def get_col_name(attr: str):
        if prop := _get_datanode_property(attr):
            return f'{attr.split(".")[0]}.{_GuiCoreScenarioProperties.__DN_NAMES.get(prop, prop)}'
        return _GuiCoreScenarioProperties.__SC_NAMES.get(attr, attr)

    def get(self):
        data = super().get()
        if _is_boolean(data):
            if _is_boolean_true(data):
                data = _GuiCoreScenarioProperties.DEFAULT
            else:
                return None
        if isinstance(data, str):
            data = data.split(";")
        if isinstance(data, (list, tuple)):
            flist = []
            for f in data:
                if f == "*":
                    flist.extend(_GuiCoreScenarioProperties.DEFAULT)
                else:
                    flist.append(f)
            if _GuiCoreScenarioProperties.__ENUMS is None:
                _GuiCoreScenarioProperties.__ENUMS = {
                    "config id": [c for c in Config.scenarios.keys() if c != "default"],
                    "tags": [t for s in Config.scenarios.values() for t in s.properties.get("authorized_tags", [])],
                }
            return json.dumps(
                [
                    (attr, _GuiCoreScenarioProperties.get_type(attr), _GuiCoreScenarioProperties.__ENUMS.get(attr))
                    for attr in flist
                    if attr and isinstance(attr, str)
                ]
            )
        return None
