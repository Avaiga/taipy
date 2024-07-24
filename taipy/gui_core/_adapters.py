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
                    if "date" in type(value).__name__.lower() or "timestamp" in type(value).__name__.lower()
                    else type(value).__name__
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


def _filter_value(base_val: t.Any, operator: t.Callable, val: t.Any, adapt: t.Optional[t.Callable] = None):
    if base_val is None:
        base_val = "" if isinstance(val, str) else 0
    else:
        if isinstance(base_val, (datetime, date)):
            base_val = base_val.isoformat()
        val = adapt(base_val, val) if adapt else val
        if isinstance(base_val, str) and isinstance(val, str):
            base_val = base_val.lower()
            val = val.lower()
    return operator(base_val, val)


def _adapt_type(base_val, val):
    # try casting the filter to the value
    if isinstance(val, str) and not isinstance(base_val, str):
        if isinstance(base_val, bool) and _is_boolean(val):
            return _is_true(val)
        else:
            try:
                return type(base_val)(val)
            except Exception:
                # forget it
                pass
    return val


def _filter_iterable(list_val: Iterable, operator: t.Callable, val: t.Any):
    if operator is contains:
        types = {type(v) for v in list_val}
        if len(types) == 1:
            typed_val = next(v for v in list_val)
            if isinstance(typed_val, (datetime, date)):
                list_val = [v.isoformat() for v in list_val]
            else:
                val = _adapt_type(typed_val, val)
        return contains(list(list_val), val)
    return next(filter(lambda v: _filter_value(v, operator, val), list_val), None) is not None


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
            if callable(col):
                cur_val = col(ent)
            else:
                cur_val = attrgetter(col_fn or col)(ent)
                cur_val = cur_val() if col_fn else cur_val
            if isinstance(cur_val, DataNode):
                cur_val = cur_val.read()
            if not isinstance(cur_val, str) and isinstance(cur_val, Iterable):
                return _filter_iterable(cur_val, op, val)
            return _filter_value(cur_val, op, val, _adapt_type)
    except Exception as e:
        if _is_debugging():
            _warn(f"Error filtering with {col} {action} {val} on {ent}.", e)
        return col_type == "any" and action == "!="
    return True


def _get_entity_property(col: str, *types: t.Type):
    col_parts = col.split("(", 2)  # handle the case where the col is a method (ie get_simple_label())
    col_fn = (
        next(
            (col_parts[0] for i in inspect.getmembers(types[0], predicate=inspect.isfunction) if i[0] == col_parts[0]),
            None,
        )
        if len(col_parts) > 1
        else None
    )

    def sort_key(entity: t.Union[Scenario, Cycle, Sequence, DataNode]):
        # we compare only strings
        if isinstance(entity, types):
            if isinstance(entity, Cycle):
                lcol = "creation_date"
                lfn = None
            else:
                lcol = col
                lfn = col_fn
            try:
                val = attrgetter(lfn or lcol)(entity)
                if lfn:
                    val = val()
            except AttributeError as e:
                if _is_debugging():
                    _warn("Attribute", e)
                val = ""
        else:
            val = ""
        return val.isoformat() if isinstance(val, (datetime, date)) else str(val)

    return sort_key


@dataclass
class _Filter(_DoNotUpdate):
    label: str
    property_type: t.Optional[t.Type]

    def get_property(self):
        return self.label

    def get_type(self):
        if self.property_type is bool:
            return "boolean"
        elif self.property_type is int or self.property_type is float:
            return "number"
        elif self.property_type is datetime or self.property_type is date:
            return "date"
        elif self.property_type is str:
            return "str"
        return "any"


@dataclass
class ScenarioFilter(_Filter):
    property_id: str

    def get_property(self):
        return self.property_id


@dataclass
class DataNodeScenarioFilter(_Filter):
    datanode_config_id: str
    property_id: str

    def get_property(self):
        return f"{self.datanode_config_id}.{self.property_id}"


_CUSTOM_PREFIX = "fn:"


@dataclass
class CustomScenarioFilter(_Filter):
    filter_function: t.Callable[[Scenario], t.Any]

    def __post_init__(self):
        if self.filter_function.__name__ == "<lambda>":
            raise TypeError("ScenarioCustomFilter does not support lambda functions.")
        mod = self.filter_function.__module__
        self.module = mod if isinstance(mod, str) else mod.__name__

    def get_property(self):
        return f"{_CUSTOM_PREFIX}{self.module}:{self.filter_function.__name__}"

    @staticmethod
    def _get_custom(col: str) -> t.Optional[t.List[str]]:
        return col[len(_CUSTOM_PREFIX) :].split(":") if col.startswith(_CUSTOM_PREFIX) else None


@dataclass
class DatanodeFilter(_Filter):
    property_id: str

    def get_property(self):
        return self.property_id


class _GuiCoreProperties(ABC):
    @staticmethod
    @abstractmethod
    def get_default_list() -> t.List[_Filter]:
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
        if isinstance(data, _Filter):
            data = (data,)
        if isinstance(data, (list, tuple)):
            flist: t.List[_Filter] = []  # type: ignore[annotation-unchecked]
            for f in data:
                if isinstance(f, str):
                    f = f.strip()
                    if f == "*":
                        flist.extend(p.filter for p in self.get_default_list())
                    elif f:
                        flist.append(
                            next((p.filter for p in self.get_default_list() if p.get_property() == f), _Filter(f))
                        )
                elif isinstance(f, _Filter):
                    flist.append(f)
            return json.dumps(
                [
                    (
                        attr.label,
                        attr.get_property(),
                        attr.get_type(),
                        self.get_enums().get(attr.get_property()),
                    )
                    if self.full_desc()
                    else (attr.label, attr.get_property())
                    for attr in flist
                ]
            )
        return None


@dataclass(frozen=True)
class _GuiCorePropDesc:
    filter: _Filter
    extended: bool = False
    for_sort: bool = False


class _GuiCoreScenarioProperties(_GuiCoreProperties):
    _SC_PROPS: t.List[_GuiCorePropDesc] = [
        _GuiCorePropDesc(ScenarioFilter("Config id", str, "config_id"), for_sort=True),
        _GuiCorePropDesc(ScenarioFilter("Label", str, "get_simple_label()"), for_sort=True),
        _GuiCorePropDesc(ScenarioFilter("Creation date", datetime, "creation_date"), for_sort=True),
        _GuiCorePropDesc(ScenarioFilter("Cycle label", str, "cycle.name"), extended=True),
        _GuiCorePropDesc(ScenarioFilter("Cycle start", datetime, "cycle.start_date"), extended=True),
        _GuiCorePropDesc(ScenarioFilter("Cycle end", datetime, "cycle.end_date"), extended=True),
        _GuiCorePropDesc(ScenarioFilter("Primary", bool, "is_primary"), extended=True),
        _GuiCorePropDesc(ScenarioFilter("Tags", str, "tags")),
    ]
    __ENUMS = None
    __SC_CYCLE = None

    @staticmethod
    def is_datanode_property(attr: str):
        if "." not in attr:
            return False
        return (
            next(
                (
                    p
                    for p in _GuiCoreScenarioProperties._SC_PROPS
                    if t.cast(ScenarioFilter, p.filter).property_id == attr
                ),
                None,
            )
            is None
        )

    def get_enums(self):
        if not self.full_desc():
            return {}
        if _GuiCoreScenarioProperties.__ENUMS is None:
            _GuiCoreScenarioProperties.__ENUMS = {
                k: v
                for k, v in {
                    "config_id": [c for c in Config.scenarios.keys() if c != "default"],
                    "tags": list(
                        {t for s in Config.scenarios.values() for t in s.properties.get("authorized_tags", [])}
                    ),
                }.items()
                if len(v)
            }

        return _GuiCoreScenarioProperties.__ENUMS

    @staticmethod
    def has_cycle():
        if _GuiCoreScenarioProperties.__SC_CYCLE is None:
            _GuiCoreScenarioProperties.__SC_CYCLE = (
                next(filter(lambda sc: sc.frequency is not None, Config.scenarios.values()), None) is not None
            )
        return _GuiCoreScenarioProperties.__SC_CYCLE


class _GuiCoreScenarioFilter(_GuiCoreScenarioProperties, _TaipyBase):
    DEFAULT = _GuiCoreScenarioProperties._SC_PROPS
    DEFAULT_NO_CYCLE = list(filter(lambda prop: not prop.extended, _GuiCoreScenarioProperties._SC_PROPS))

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
    DEFAULT = list(filter(lambda prop: prop.for_sort, _GuiCoreScenarioProperties._SC_PROPS))
    DEFAULT_NO_CYCLE = list(
        filter(lambda prop: prop.for_sort and not prop.extended, _GuiCoreScenarioProperties._SC_PROPS)
    )

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
    _DN_PROPS: t.List[_GuiCorePropDesc] = [
        _GuiCorePropDesc(DatanodeFilter("Config id", str, "config_id"), for_sort=True),
        _GuiCorePropDesc(DatanodeFilter("Label", str, "get_simple_label()"), for_sort=True),
        _GuiCorePropDesc(DatanodeFilter("Up to date", bool, "is_up_to_date")),
        _GuiCorePropDesc(DatanodeFilter("Last edit date", datetime, "last_edit_date"), for_sort=True),
        _GuiCorePropDesc(DatanodeFilter("Input", bool, "is_input")),
        _GuiCorePropDesc(DatanodeFilter("Output", bool, "is_output")),
        _GuiCorePropDesc(DatanodeFilter("Intermediate", bool, "is_intermediate")),
        _GuiCorePropDesc(DatanodeFilter("Expiration date", datetime, "expiration_date"), extended=True, for_sort=True),
        _GuiCorePropDesc(DatanodeFilter("Expired", bool, "is_expired"), extended=True),
    ]
    __DN_VALIDITY = None

    @staticmethod
    def has_validity():
        if _GuiCoreDatanodeProperties.__DN_VALIDITY is None:
            _GuiCoreDatanodeProperties.__DN_VALIDITY = (
                next(filter(lambda dn: dn.validity_period is not None, Config.data_nodes.values()), None) is not None
            )
        return _GuiCoreDatanodeProperties.__DN_VALIDITY


class _GuiCoreDatanodeFilter(_GuiCoreDatanodeProperties, _TaipyBase):
    DEFAULT = _GuiCoreDatanodeProperties._DN_PROPS
    DEFAULT_NO_VALIDITY = list(filter(lambda prop: not prop.extended, _GuiCoreDatanodeProperties._DN_PROPS))

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
    DEFAULT = list(filter(lambda prop: prop.for_sort, _GuiCoreDatanodeProperties._DN_PROPS))
    DEFAULT_NO_VALIDITY = list(
        filter(lambda prop: prop.for_sort and not prop.extended, _GuiCoreDatanodeProperties._DN_PROPS)
    )

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
