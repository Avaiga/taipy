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
import sys
import typing as t
from abc import ABC, abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum
from numbers import Number
from operator import attrgetter, contains, eq, ge, gt, le, lt, ne

import pandas as pd

from taipy.core import (
    Cycle,
    DataNode,
    Scenario,
    Sequence,
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
from taipy.gui.utils import _is_boolean, _is_true, _TaipyBase


# prevent gui from trying to push scenario instances to the front-end
class _GuiCoreDoNotUpdate(_DoNotUpdate):
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
                                "" if (reason := is_submittable(s)) else f"Sequence not submittable: {reason.reasons}",
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
                        "" if (reason := is_submittable(scenario)) else f"Scenario not submittable: {reason.reasons}",
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

def _filter_iterable(lval: Iterable, op: t.Callable, val: t.Any):
    return next(filter(lambda v: op(v, val), lval), None) is not None

def _invoke_action(
    ent: t.Any, col: str, col_type: str, is_dn: bool, action: str, val: t.Any, col_fn: t.Optional[str]
) -> bool:
    if ent is None:
        return False
    try:
        if col_type == "any":
            # when a property is not found, return True only if action is not equals
            if not is_dn and not hasattr(ent, "properties") or not ent.properties.get(col_fn or col):
                return action == "!="
        if op := _operators.get(action):
            cur_val = attrgetter(col_fn or col)(ent)
            cur_val = cur_val() if col_fn else cur_val
            if isinstance(cur_val, Iterable):
                return _filter_iterable(cur_val, op, val)
            return op(cur_val.isoformat() if isinstance(cur_val, (datetime, date)) else cur_val, val)
    except Exception as e:
        if _is_debugging():
            _warn(f"Error filtering with {col} {action} {val} on {ent}.", e)
        return col_type == "any" and action == "!="
    return True


def _get_entity_property(col: str, a_type: t.Type):
    col_parts = col.split("(")  # handle the case where the col is a method (ie get_simple_label())
    col_fn = (
        next(
            (col_parts[0] for i in inspect.getmembers(a_type, predicate=inspect.isfunction) if i[0] == col_parts[0]),
            None,
        )
        if len(col_parts) > 1
        else None
    )

    def sort_key(entity: t.Union[Scenario, Cycle, Sequence, DataNode]):
        # we compare only strings
        if isinstance(entity, a_type):
            try:
                val = attrgetter(col_fn or col)(entity)
                if col_fn:
                    val = val()
            except AttributeError as e:
                if _is_debugging():
                    _warn("Attribute", e)
                val = ""
        else:
            val = ""
        return val.isoformat() if isinstance(val, (datetime, date)) else str(val)

    return sort_key


def _get_datanode_property(attr: str):
    if (parts := attr.split(".")) and len(parts) > 1:
        return parts[1]
    return None


class _GuiCoreProperties(ABC):
    @staticmethod
    @abstractmethod
    def get_type(attr: str):
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def get_col_name(attr: str):
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def get_default_list():
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def full_desc():
        raise NotImplementedError

    def get_enums(self):
        return {}

    def get(self):
        data = super().get()
        if _is_boolean(data):
            if _is_true(data):
                data = self.get_default_list()
            else:
                return None
        if isinstance(data, str):
            data = data.split(";")
        if isinstance(data, (list, tuple)):
            flist = []
            for f in data:
                if f == "*":
                    flist.extend(self.get_default_list())
                else:
                    flist.append(f)
            return json.dumps(
                [
                    (attr, self.get_type(attr), self.get_enums().get(attr)) if self.full_desc() else (attr,)
                    for attr in flist
                    if attr and isinstance(attr, str)
                ]
            )
        return None


@dataclass(frozen=True)
class _GuiCorePropDesc:
    attr: str
    type: str
    extended: bool = False
    for_sort: bool = False


_EMPTY_PROP_DESC = _GuiCorePropDesc("", "any")


class _GuiCoreScenarioProperties(_GuiCoreProperties):
    _SC_PROPS: t.Dict[str, _GuiCorePropDesc] = {
        "Config id": _GuiCorePropDesc("config_id", "string", for_sort=True),
        "Label": _GuiCorePropDesc("get_simple_label()", "string", for_sort=True),
        "Creation date": _GuiCorePropDesc("creation_date", "date", for_sort=True),
        "Cycle label": _GuiCorePropDesc("cycle.name", "string", extended=True),
        "Cycle start": _GuiCorePropDesc("cycle.start_date", "date", extended=True),
        "Cycle end": _GuiCorePropDesc("cycle.end_date", "date", extended=True),
        "Primary": _GuiCorePropDesc("is_primary", "boolean", extended=True),
        "Tags": _GuiCorePropDesc("tags", "string"),
    }
    __DN_PROPS = {
        "Up to date": _GuiCorePropDesc("is_up_to_date", "boolean"),
        "Valid": _GuiCorePropDesc("is_valid", "boolean"),
        "Last edit date": _GuiCorePropDesc("last_edit_date", "date"),
    }
    __ENUMS = None
    __SC_CYCLE = None

    @staticmethod
    def get_type(attr: str):
        if prop := _get_datanode_property(attr):
            return _GuiCoreScenarioProperties.__DN_PROPS.get(prop, _EMPTY_PROP_DESC).type
        return _GuiCoreScenarioProperties._SC_PROPS.get(attr, _EMPTY_PROP_DESC).type

    @staticmethod
    def get_col_name(attr: str):
        if prop := _get_datanode_property(attr):
            return (
                attr.split(".")[0]
                + f".{_GuiCoreScenarioProperties.__DN_PROPS.get(prop, _EMPTY_PROP_DESC).attr or prop}"
            )
        return _GuiCoreScenarioProperties._SC_PROPS.get(attr, _EMPTY_PROP_DESC).attr or attr

    def get_enums(self):
        if _GuiCoreScenarioProperties.__ENUMS is None:
            _GuiCoreScenarioProperties.__ENUMS = {
                k: v
                for k, v in {
                    "Config id": [c for c in Config.scenarios.keys() if c != "default"],
                    "Tags": list(
                        {t for s in Config.scenarios.values() for t in s.properties.get("authorized_tags", [])}
                    ),
                }.items()
                if len(v)
            }

        return _GuiCoreScenarioProperties.__ENUMS if self.full_desc() else {}

    @staticmethod
    def has_cycle():
        if _GuiCoreScenarioProperties.__SC_CYCLE is None:
            _GuiCoreScenarioProperties.__SC_CYCLE = (
                next(filter(lambda sc: sc.frequency is not None, Config.scenarios.values()), None) is not None
            )
        return _GuiCoreScenarioProperties.__SC_CYCLE


class _GuiCoreScenarioFilter(_GuiCoreScenarioProperties, _TaipyBase):
    DEFAULT = list(_GuiCoreScenarioProperties._SC_PROPS.keys())
    DEFAULT_NO_CYCLE = [
        p[0] for p in filter(lambda prop: not prop[1].extended, _GuiCoreScenarioProperties._SC_PROPS.items())
    ]

    @staticmethod
    def full_desc():
        return True

    @staticmethod
    def get_hash():
        return _TaipyBase._HOLDER_PREFIX + "ScF"

    @staticmethod
    def get_default_list():
        return (
            _GuiCoreScenarioFilter.DEFAULT
            if _GuiCoreScenarioProperties.has_cycle()
            else _GuiCoreScenarioFilter.DEFAULT_NO_CYCLE
        )


class _GuiCoreScenarioSort(_GuiCoreScenarioProperties, _TaipyBase):
    DEFAULT = [p[0] for p in filter(lambda prop: prop[1].for_sort, _GuiCoreScenarioProperties._SC_PROPS.items())]
    DEFAULT_NO_CYCLE = [
        p[0]
        for p in filter(
            lambda prop: prop[1].for_sort and not prop[1].extended, _GuiCoreScenarioProperties._SC_PROPS.items()
        )
    ]

    @staticmethod
    def full_desc():
        return False

    @staticmethod
    def get_hash():
        return _TaipyBase._HOLDER_PREFIX + "ScS"

    @staticmethod
    def get_default_list():
        return (
            _GuiCoreScenarioSort.DEFAULT
            if _GuiCoreScenarioProperties.has_cycle()
            else _GuiCoreScenarioSort.DEFAULT_NO_CYCLE
        )


class _GuiCoreDatanodeProperties(_GuiCoreProperties):
    _DN_PROPS: t.Dict[str, _GuiCorePropDesc] = {
        "Config id": _GuiCorePropDesc("config_id", "string", for_sort=True),
        "Label": _GuiCorePropDesc("get_simple_label()", "string", for_sort=True),
        "Up to date": _GuiCorePropDesc("is_up_to_date", "boolean"),
        "Last edit date": _GuiCorePropDesc("last_edit_date", "date", for_sort=True),
        "Input": _GuiCorePropDesc("is_input", "boolean"),
        "Output": _GuiCorePropDesc("is_output", "boolean"),
        "Intermediate": _GuiCorePropDesc("is_intermediate", "boolean"),
        "Expiration date": _GuiCorePropDesc("expiration_date", "date", extended=True, for_sort=True),
        "Expired": _GuiCorePropDesc("is_expired", "boolean", extended=True),
    }
    __DN_VALIDITY = None

    @staticmethod
    def get_type(attr: str):
        return _GuiCoreDatanodeProperties._DN_PROPS.get(attr, _EMPTY_PROP_DESC).type

    @staticmethod
    def get_col_name(attr: str):
        return _GuiCoreDatanodeProperties._DN_PROPS.get(attr, _EMPTY_PROP_DESC).attr or attr

    @staticmethod
    def has_validity():
        if _GuiCoreDatanodeProperties.__DN_VALIDITY is None:
            _GuiCoreDatanodeProperties.__DN_VALIDITY = (
                next(filter(lambda dn: dn.validity_period is not None, Config.data_nodes.values()), None) is not None
            )
        return _GuiCoreDatanodeProperties.__DN_VALIDITY


class _GuiCoreDatanodeFilter(_GuiCoreDatanodeProperties, _TaipyBase):
    DEFAULT = list(_GuiCoreDatanodeProperties._DN_PROPS.keys())
    DEFAULT_NO_VALIDITY = [
        p[0] for p in filter(lambda prop: not prop[1].extended, _GuiCoreDatanodeProperties._DN_PROPS.items())
    ]

    @staticmethod
    def full_desc():
        return True

    @staticmethod
    def get_hash():
        return _TaipyBase._HOLDER_PREFIX + "DnF"

    @staticmethod
    def get_default_list():
        return (
            _GuiCoreDatanodeFilter.DEFAULT
            if _GuiCoreDatanodeProperties.has_validity()
            else _GuiCoreDatanodeFilter.DEFAULT_NO_VALIDITY
        )


class _GuiCoreDatanodeSort(_GuiCoreDatanodeProperties, _TaipyBase):
    DEFAULT = [p[0] for p in filter(lambda prop: prop[1].for_sort, _GuiCoreDatanodeProperties._DN_PROPS.items())]
    DEFAULT_NO_VALIDITY = [
        p[0]
        for p in filter(
            lambda prop: prop[1].for_sort and not prop[1].extended, _GuiCoreDatanodeProperties._DN_PROPS.items()
        )
    ]

    @staticmethod
    def full_desc():
        return False

    @staticmethod
    def get_hash():
        return _TaipyBase._HOLDER_PREFIX + "DnS"

    @staticmethod
    def get_default_list():
        return (
            _GuiCoreDatanodeSort.DEFAULT
            if _GuiCoreDatanodeProperties.has_validity()
            else _GuiCoreDatanodeSort.DEFAULT_NO_VALIDITY
        )


def _is_debugging() -> bool:
    return hasattr(sys, "gettrace") and sys.gettrace() is not None
