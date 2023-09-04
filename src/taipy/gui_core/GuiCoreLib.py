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

import json
import typing as t
from collections import defaultdict
from datetime import datetime
from enum import Enum
from numbers import Number
from threading import Lock

try:
    import zoneinfo
except ImportError:
    from backports import zoneinfo  # type: ignore[no-redef]

import pandas as pd
from dateutil import parser

from taipy.config import Config
from taipy.core import Cycle, DataNode, Job, Scenario, Sequence, cancel_job, create_scenario
from taipy.core import delete as core_delete
from taipy.core import delete_job
from taipy.core import get as core_get
from taipy.core import (
    get_cycles_scenarios,
    get_data_nodes,
    get_jobs,
    is_deletable,
    is_promotable,
    is_submittable,
    set_primary,
)
from taipy.core import submit as core_submit
from taipy.core.data._abstract_tabular import _AbstractTabularDataNode
from taipy.core.notification import CoreEventConsumerBase, EventEntityType
from taipy.core.notification.event import Event
from taipy.core.notification.notifier import Notifier
from taipy.gui import Gui, State
from taipy.gui._warnings import _warn
from taipy.gui.extension import Element, ElementLibrary, ElementProperty, PropertyType
from taipy.gui.gui import _DoNotUpdate
from taipy.gui.utils import _TaipyBase

from ..version import _get_version


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
                    is_deletable(scenario),  # deletable
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
                ]
        return None

    @staticmethod
    def get_hash():
        return _TaipyBase._HOLDER_PREFIX + "Dn"


class _GuiCoreContext(CoreEventConsumerBase):
    __PROP_ENTITY_ID = "id"
    __PROP_CONFIG_ID = "config"
    __PROP_DATE = "date"
    __PROP_ENTITY_NAME = "name"
    __PROP_SCENARIO_PRIMARY = "primary"
    __PROP_SCENARIO_TAGS = "tags"
    __ENTITY_PROPS = (__PROP_CONFIG_ID, __PROP_DATE, __PROP_ENTITY_NAME)
    __ACTION = "action"
    _CORE_CHANGED_NAME = "core_changed"
    _SCENARIO_SELECTOR_ERROR_VAR = "gui_core_sc_error"
    _SCENARIO_SELECTOR_ID_VAR = "gui_core_sc_id"
    _SCENARIO_VIZ_ERROR_VAR = "gui_core_sv_error"
    _JOB_SELECTOR_ERROR_VAR = "gui_core_js_error"
    _DATANODE_VIZ_ERROR_VAR = "gui_core_dv_error"
    _DATANODE_VIZ_OWNER_ID_VAR = "gui_core_dv_owner_id"
    _DATANODE_VIZ_HISTORY_ID_VAR = "gui_core_dv_history_id"
    _DATANODE_VIZ_DATA_ID_VAR = "gui_core_dv_data_id"
    _DATANODE_VIZ_DATA_CHART_ID_VAR = "gui_core_dv_data_chart_id"
    _DATANODE_VIZ_DATA_NODE_PROP = "data_node"

    def __init__(self, gui: Gui) -> None:
        self.gui = gui
        self.scenario_by_cycle: t.Optional[t.Dict[t.Optional[Cycle], t.List[Scenario]]] = None
        self.data_nodes_by_owner: t.Optional[t.Dict[t.Optional[str], DataNode]] = None
        self.scenario_configs: t.Optional[t.List[t.Tuple[str, str]]] = None
        self.jobs_list: t.Optional[t.List[Job]] = None
        # register to taipy core notification
        reg_id, reg_queue = Notifier.register()
        self.lock = Lock()
        super().__init__(reg_id, reg_queue)
        self.start()

    def process_event(self, event: Event):
        if event.entity_type == EventEntityType.SCENARIO:
            with self.lock:
                self.scenario_by_cycle = None
                self.data_nodes_by_owner = None
            scenario = core_get(event.entity_id) if event.operation.value != 3 else None
            self.gui.broadcast(
                _GuiCoreContext._CORE_CHANGED_NAME,
                {"scenario": event.entity_id if scenario else True},
            )
        elif event.entity_type == EventEntityType.SEQUENCE and event.entity_id:  # TODO import EventOperation
            sequence = core_get(event.entity_id) if event.operation.value != 3 else None
            if sequence:
                if hasattr(sequence, "parent_ids") and sequence.parent_ids:
                    self.gui.broadcast(
                        _GuiCoreContext._CORE_CHANGED_NAME, {"scenario": [x for x in sequence.parent_ids]}
                    )
        elif event.entity_type == EventEntityType.JOB:
            with self.lock:
                self.jobs_list = None
            self.gui.broadcast(_GuiCoreContext._CORE_CHANGED_NAME, {"jobs": True})
        elif event.entity_type == EventEntityType.DATA_NODE:
            with self.lock:
                self.data_nodes_by_owner = None
            self.gui.broadcast(
                _GuiCoreContext._CORE_CHANGED_NAME,
                {"datanode": event.entity_id if event.operation.value != 3 else True},
            )

    def scenario_adapter(self, data):
        if hasattr(data, "id") and core_get(data.id) is not None:
            if self.scenario_by_cycle and isinstance(data, Cycle):
                return (
                    data.id,
                    data.get_simple_label(),
                    self.scenario_by_cycle.get(data),
                    _EntityType.CYCLE.value,
                    False,
                )
            elif isinstance(data, Scenario):
                return (data.id, data.get_simple_label(), None, _EntityType.SCENARIO.value, data.is_primary)
        return None

    def get_scenarios(self):
        cycles_scenarios = []
        with self.lock:
            if self.scenario_by_cycle is None:
                self.scenario_by_cycle = get_cycles_scenarios()
            for cycle, scenarios in self.scenario_by_cycle.items():
                if cycle is None:
                    cycles_scenarios.extend(scenarios)
                else:
                    cycles_scenarios.append(cycle)
        return cycles_scenarios

    def select_scenario(self, state: State, id: str, action: str, payload: t.Dict[str, str]):
        args = payload.get("args")
        if args is None or not isinstance(args, list) or len(args) == 0:
            return
        state.assign(_GuiCoreContext._SCENARIO_SELECTOR_ID_VAR, args[0])

    def get_scenario_by_id(self, id: str) -> t.Optional[Scenario]:
        if not id:
            return None
        try:
            return core_get(id)
        except Exception:
            return None

    def get_scenario_configs(self):
        with self.lock:
            if self.scenario_configs is None:
                configs = Config.scenarios
                if isinstance(configs, dict):
                    self.scenario_configs = [(id, f"{c.id}") for id, c in configs.items() if id != "default"]
            return self.scenario_configs

    def crud_scenario(self, state: State, id: str, user_action: str, payload: t.Dict[str, str]):  # noqa: C901
        args = payload.get("args")
        if (
            args is None
            or not isinstance(args, list)
            or len(args) < 3
            or not isinstance(args[0], bool)
            or not isinstance(args[1], bool)
            or not isinstance(args[2], dict)
        ):
            return
        update = args[0]
        delete = args[1]
        data = args[2]
        scenario = None

        name = data.get(_GuiCoreContext.__PROP_ENTITY_NAME)
        if update:
            scenario_id = data.get(_GuiCoreContext.__PROP_ENTITY_ID)
            if delete:
                try:
                    core_delete(scenario_id)
                except Exception as e:
                    state.assign(_GuiCoreContext._SCENARIO_SELECTOR_ERROR_VAR, f"Error deleting Scenario. {e}")
            else:
                scenario = core_get(scenario_id)
        else:
            config_id = data.get(_GuiCoreContext.__PROP_CONFIG_ID)
            scenario_config = Config.scenarios.get(config_id)
            if scenario_config is None:
                state.assign(_GuiCoreContext._SCENARIO_SELECTOR_ERROR_VAR, f"Invalid configuration id ({config_id})")
                return
            date_str = data.get(_GuiCoreContext.__PROP_DATE)
            try:
                date = parser.parse(date_str) if isinstance(date_str, str) else None
            except Exception as e:
                state.assign(_GuiCoreContext._SCENARIO_SELECTOR_ERROR_VAR, f"Invalid date ({date_str}).{e}")
                return
            try:
                gui: Gui = state._gui
                on_creation = args[3] if len(args) > 3 and isinstance(args[3], str) else None
                on_creation_function = gui._get_user_function(on_creation) if on_creation else None
                if callable(on_creation_function):
                    try:
                        res = gui._call_function_with_state(
                            on_creation_function,
                            [
                                id,
                                on_creation,
                                {
                                    "config": scenario_config,
                                    "date": date,
                                    "label": name,
                                    "properties": {
                                        v.get("key"): v.get("value") for v in data.get("properties", dict())
                                    },
                                },
                            ],
                        )
                        if isinstance(res, Scenario):
                            # everything's fine
                            state.assign(_GuiCoreContext._SCENARIO_SELECTOR_ERROR_VAR, "")
                            return
                        if res:
                            # do not create
                            state.assign(_GuiCoreContext._SCENARIO_SELECTOR_ERROR_VAR, f"{res}")
                            return
                    except Exception as e:  # pragma: no cover
                        if not gui._call_on_exception(on_creation, e):
                            _warn(f"on_creation(): Exception raised in '{on_creation}()':\n{e}")
                else:
                    _warn(f"on_creation(): '{on_creation}' is not a function.")
                scenario = create_scenario(scenario_config, date, name)
            except Exception as e:
                state.assign(_GuiCoreContext._SCENARIO_SELECTOR_ERROR_VAR, f"Error creating Scenario. {e}")
        if scenario:
            with scenario as sc:
                sc.properties[_GuiCoreContext.__PROP_ENTITY_NAME] = name
                if props := data.get("properties"):
                    try:
                        new_keys = [prop.get("key") for prop in props]
                        for key in t.cast(dict, sc.properties).keys():
                            if key and key not in _GuiCoreContext.__ENTITY_PROPS and key not in new_keys:
                                t.cast(dict, sc.properties).pop(key, None)
                        for prop in props:
                            key = prop.get("key")
                            if key and key not in _GuiCoreContext.__ENTITY_PROPS:
                                sc._properties[key] = prop.get("value")
                        state.assign(_GuiCoreContext._SCENARIO_SELECTOR_ERROR_VAR, "")
                    except Exception as e:
                        state.assign(_GuiCoreContext._SCENARIO_SELECTOR_ERROR_VAR, f"Error creating Scenario. {e}")

    def edit_entity(self, state: State, id: str, action: str, payload: t.Dict[str, str]):
        args = payload.get("args")
        if args is None or not isinstance(args, list) or len(args) < 1 or not isinstance(args[0], dict):
            return
        data = args[0]
        entity_id = data.get(_GuiCoreContext.__PROP_ENTITY_ID)
        entity: t.Union[Scenario, Sequence] = core_get(entity_id)
        if entity:
            try:
                if isinstance(entity, Scenario):
                    primary = data.get(_GuiCoreContext.__PROP_SCENARIO_PRIMARY)
                    if primary is True:
                        set_primary(entity)
                self.__edit_properties(entity, data)
                state.assign(_GuiCoreContext._SCENARIO_VIZ_ERROR_VAR, "")
            except Exception as e:
                state.assign(_GuiCoreContext._SCENARIO_VIZ_ERROR_VAR, f"Error updating Scenario. {e}")

    def submit_entity(self, state: State, id: str, action: str, payload: t.Dict[str, str]):
        args = payload.get("args")
        if args is None or not isinstance(args, list) or len(args) < 1 or not isinstance(args[0], dict):
            return
        data = args[0]
        entity_id = data.get(_GuiCoreContext.__PROP_ENTITY_ID)
        entity = core_get(entity_id)
        if entity:
            try:
                core_submit(entity)
                state.assign(_GuiCoreContext._SCENARIO_VIZ_ERROR_VAR, "")
            except Exception as e:
                state.assign(_GuiCoreContext._SCENARIO_VIZ_ERROR_VAR, f"Error submitting entity. {e}")

    def __do_datanodes_tree(self):
        if self.data_nodes_by_owner is None:
            self.data_nodes_by_owner = defaultdict(list)
            for dn in get_data_nodes():
                self.data_nodes_by_owner[dn.owner_id].append(dn)

    def get_datanodes_tree(self):
        with self.lock:
            self.__do_datanodes_tree()
        return self.get_scenarios()

    def data_node_adapter(self, data):
        if data and hasattr(data, "id") and core_get(data.id) is not None:
            if isinstance(data, DataNode):
                return (data.id, data.get_simple_label(), None, _EntityType.DATANODE.value, False)
            else:
                with self.lock:
                    self.__do_datanodes_tree()
                    if self.data_nodes_by_owner:
                        if isinstance(data, Cycle):
                            return (
                                data.id,
                                data.get_simple_label(),
                                self.data_nodes_by_owner[data.id] + self.scenario_by_cycle.get(data, []),
                                _EntityType.CYCLE.value,
                                False,
                            )
                        elif isinstance(data, Scenario):
                            return (
                                data.id,
                                data.get_simple_label(),
                                self.data_nodes_by_owner[data.id] + list(data.sequences.values()),
                                _EntityType.SCENARIO.value,
                                data.is_primary,
                            )
                        elif isinstance(data, Sequence):
                            if datanodes := self.data_nodes_by_owner.get(data.id):
                                return (data.id, data.get_simple_label(), datanodes, _EntityType.SEQUENCE.value, False)
        return None

    def get_jobs_list(self):
        with self.lock:
            if self.jobs_list is None:
                self.jobs_list = get_jobs()
            return self.jobs_list

    def job_adapter(self, data):
        if hasattr(data, "id") and core_get(data.id) is not None:
            if isinstance(data, Job):
                # entity = core_get(data.owner_id)
                return (
                    data.id,
                    data.get_simple_label(),
                    [],
                    "",
                    "",
                    data.submit_id,
                    data.creation_date,
                    data.status.value,
                )

    def act_on_jobs(self, state: State, id: str, action: str, payload: t.Dict[str, str]):
        args = payload.get("args")
        if args is None or not isinstance(args, list) or len(args) < 1 or not isinstance(args[0], dict):
            return
        data = args[0]
        job_ids = data.get(_GuiCoreContext.__PROP_ENTITY_ID)
        job_action = data.get(_GuiCoreContext.__ACTION)
        if job_action and isinstance(job_ids, list):
            errs = []
            if job_action == "delete":
                for job_id in job_ids:
                    try:
                        delete_job(core_get(job_id))
                    except Exception as e:
                        errs.append(f"Error deleting job. {e}")
            elif job_action == "cancel":
                for job_id in job_ids:
                    try:
                        cancel_job(job_id)
                    except Exception as e:
                        errs.append(f"Error canceling job. {e}")
            state.assign(_GuiCoreContext._JOB_SELECTOR_ERROR_VAR, "<br/>".join(errs) if errs else "")

    def edit_data_node(self, state: State, id: str, action: str, payload: t.Dict[str, str]):
        args = payload.get("args")
        if args is None or not isinstance(args, list) or len(args) < 1 or not isinstance(args[0], dict):
            return
        data = args[0]
        entity_id = data.get(_GuiCoreContext.__PROP_ENTITY_ID)
        entity: DataNode = core_get(entity_id)
        if isinstance(entity, DataNode):
            try:
                self.__edit_properties(entity, data)
                state.assign(_GuiCoreContext._DATANODE_VIZ_ERROR_VAR, "")
            except Exception as e:
                state.assign(_GuiCoreContext._DATANODE_VIZ_ERROR_VAR, f"Error updating Datanode. {e}")

    def __edit_properties(self, entity: t.Union[Scenario, Sequence, DataNode], data: t.Dict[str, str]):
        with entity as ent:
            if isinstance(ent, Scenario):
                tags = data.get(_GuiCoreContext.__PROP_SCENARIO_TAGS)
                if isinstance(tags, (list, tuple)):
                    ent.tags = {t for t in tags}
            name = data.get(_GuiCoreContext.__PROP_ENTITY_NAME)
            if isinstance(name, str):
                ent.properties[_GuiCoreContext.__PROP_ENTITY_NAME] = name
            props = data.get("properties")
            if isinstance(props, (list, tuple)):
                for prop in props:
                    key = prop.get("key")
                    if key and key not in _GuiCoreContext.__ENTITY_PROPS:
                        ent.properties[key] = prop.get("value")
            deleted_props = data.get("deleted_properties")
            if isinstance(deleted_props, (list, tuple)):
                for prop in deleted_props:
                    key = prop.get("key")
                    if key and key not in _GuiCoreContext.__ENTITY_PROPS:
                        ent.properties.pop(key, None)

    def get_scenarios_for_owner(self, owner_id: str):
        cycles_scenarios: t.List[t.Union[Scenario, Cycle]] = []
        with self.lock:
            if self.scenario_by_cycle is None:
                self.scenario_by_cycle = get_cycles_scenarios()
            if owner_id:
                if owner_id == "GLOBAL":
                    for cycle, scenarios in self.scenario_by_cycle.items():
                        if cycle is None:
                            cycles_scenarios.extend(scenarios)
                        else:
                            cycles_scenarios.append(cycle)
                else:
                    entity = core_get(owner_id)
                    if entity and (scenarios := self.scenario_by_cycle.get(entity)):
                        cycles_scenarios.extend(scenarios)
                    elif isinstance(entity, Scenario):
                        cycles_scenarios.append(entity)
        return cycles_scenarios

    def get_data_node_history(self, datanode: DataNode, id: str):
        if (
            id
            and isinstance(datanode, DataNode)
            and id == datanode.id
            and (dn := core_get(id))
            and isinstance(dn, DataNode)
        ):
            res = []
            for e in dn.edits:
                job: Job = core_get(e.get("job_id")) if "job_id" in e else None
                res.append(
                    (
                        e.get("timestamp"),
                        job.id if job else e.get("writer_identifier", "Unknown"),
                        f"Execution of task {job.task.get_simple_label()}." if job and job.task else e.get("comments"),
                    )
                )
            return list(reversed(sorted(res, key=lambda r: r[0])))
        return _DoNotUpdate()

    def get_data_node_data(self, datanode: DataNode, id: str):
        if (
            id
            and isinstance(datanode, DataNode)
            and id == datanode.id
            and (dn := core_get(id))
            and isinstance(dn, DataNode)
        ):
            if dn.is_ready_for_reading:
                if isinstance(dn, _AbstractTabularDataNode):
                    return (None, None, True, None)
                try:
                    value = dn.read()
                    if isinstance(value, (pd.DataFrame, pd.Series)):
                        return (None, None, True, None)
                    return (
                        value,
                        "date"
                        if "date" in type(value).__name__
                        else type(value).__name__
                        if isinstance(value, Number)
                        else None,
                        None,
                        None,
                    )
                except Exception as e:
                    return (None, None, None, f"read data_node: {e}")
            return (None, None, None, f"Data unavailable for {dn.get_simple_label()}")
        return _DoNotUpdate()

    def update_data(self, state: State, id: str, action: str, payload: t.Dict[str, str]):
        args = payload.get("args")
        if args is None or not isinstance(args, list) or len(args) < 1 or not isinstance(args[0], dict):
            return
        data = args[0]
        entity_id = data.get(_GuiCoreContext.__PROP_ENTITY_ID)
        entity: DataNode = core_get(entity_id)
        if isinstance(entity, DataNode):
            try:
                entity.write(
                    parser.parse(data.get("value"))
                    if data.get("type") == "date"
                    else int(data.get("value"))
                    if data.get("type") == "int"
                    else float(data.get("value"))
                    if data.get("type") == "float"
                    else data.get("value"),
                    comment="Written by CoreGui DataNode viewer Element",
                )
                state.assign(_GuiCoreContext._DATANODE_VIZ_ERROR_VAR, "")
            except Exception as e:
                state.assign(_GuiCoreContext._DATANODE_VIZ_ERROR_VAR, f"Error updating Datanode value. {e}")
            state.assign(_GuiCoreContext._DATANODE_VIZ_DATA_ID_VAR, entity_id)  # this will update the data value

    def tabular_data_edit(self, state: State, var_name: str, action: str, payload: dict):
        dn_id = payload.get("user_data")
        datanode = core_get(dn_id)
        if isinstance(datanode, DataNode):
            try:
                idx = payload.get("index")
                col = payload.get("col")
                tz = payload.get("tz")
                val = (
                    parser.parse(str(payload.get("value"))).astimezone(zoneinfo.ZoneInfo(tz)).replace(tzinfo=None)
                    if tz is not None
                    else payload.get("value")
                )
                # user_value = payload.get("user_value")
                data = self.__read_tabular_data(datanode)
                data.at[idx, col] = val
                datanode.write(data)
                state.assign(_GuiCoreContext._DATANODE_VIZ_ERROR_VAR, "")
            except Exception as e:
                state.assign(_GuiCoreContext._DATANODE_VIZ_ERROR_VAR, f"Error updating Datanode tabular value. {e}")
        setattr(state, _GuiCoreContext._DATANODE_VIZ_DATA_ID_VAR, dn_id)

    def __read_tabular_data(self, datanode: DataNode):
        return datanode.read()

    def get_data_node_tabular_data(self, datanode: DataNode, id: str):
        if (
            id
            and isinstance(datanode, DataNode)
            and id == datanode.id
            and (dn := core_get(id))
            and isinstance(dn, DataNode)
            and dn.is_ready_for_reading
        ):
            try:
                return self.__read_tabular_data(dn)
            except Exception:
                return None
        return None

    def get_data_node_tabular_columns(self, datanode: DataNode, id: str):
        if (
            id
            and isinstance(datanode, DataNode)
            and id == datanode.id
            and (dn := core_get(id))
            and isinstance(dn, DataNode)
            and dn.is_ready_for_reading
        ):
            try:
                return self.gui._tbl_cols(
                    True, True, "{}", json.dumps({"data": "tabular_data"}), tabular_data=self.__read_tabular_data(dn)
                )
            except Exception:
                return None
        return None

    def get_data_node_chart_config(self, datanode: DataNode, id: str):
        if (
            id
            and isinstance(datanode, DataNode)
            and id == datanode.id
            and (dn := core_get(id))
            and isinstance(dn, DataNode)
            and dn.is_ready_for_reading
        ):
            try:
                return self.gui._chart_conf(
                    True, True, "{}", json.dumps({"data": "tabular_data"}), tabular_data=self.__read_tabular_data(dn)
                )
            except Exception:
                return None
        return None

    def select_id(self, state: State, id: str, action: str, payload: t.Dict[str, str]):
        args = payload.get("args")
        if args is None or not isinstance(args, list) or len(args) == 0 and isinstance(args[0], dict):
            return
        data = args[0]
        if owner_id := data.get("owner_id"):
            state.assign(_GuiCoreContext._DATANODE_VIZ_OWNER_ID_VAR, owner_id)
        elif history_id := data.get("history_id"):
            state.assign(_GuiCoreContext._DATANODE_VIZ_HISTORY_ID_VAR, history_id)
        elif data_id := data.get("data_id"):
            state.assign(_GuiCoreContext._DATANODE_VIZ_DATA_ID_VAR, data_id)
        elif chart_id := data.get("chart_id"):
            state.assign(_GuiCoreContext._DATANODE_VIZ_DATA_CHART_ID_VAR, chart_id)


class _GuiCore(ElementLibrary):
    __LIB_NAME = "taipy_gui_core"
    __CTX_VAR_NAME = f"__{__LIB_NAME}_Ctx"
    __SCENARIO_ADAPTER = "tgc_scenario"
    __DATANODE_ADAPTER = "tgc_datanode"
    __JOB_ADAPTER = "tgc_job"

    __elts = {
        "scenario_selector": Element(
            "value",
            {
                "id": ElementProperty(PropertyType.string),
                "show_add_button": ElementProperty(PropertyType.boolean, True),
                "display_cycles": ElementProperty(PropertyType.boolean, True),
                "show_primary_flag": ElementProperty(PropertyType.boolean, True),
                "value": ElementProperty(PropertyType.lov_value),
                "on_change": ElementProperty(PropertyType.function),
                "height": ElementProperty(PropertyType.string, "50vh"),
                "class_name": ElementProperty(PropertyType.dynamic_string),
                "show_pins": ElementProperty(PropertyType.boolean, False),
                "on_creation": ElementProperty(PropertyType.function),
            },
            inner_properties={
                "scenarios": ElementProperty(PropertyType.lov, f"{{{__CTX_VAR_NAME}.get_scenarios()}}"),
                "on_scenario_crud": ElementProperty(PropertyType.function, f"{{{__CTX_VAR_NAME}.crud_scenario}}"),
                "configs": ElementProperty(PropertyType.react, f"{{{__CTX_VAR_NAME}.get_scenario_configs()}}"),
                "core_changed": ElementProperty(PropertyType.broadcast, _GuiCoreContext._CORE_CHANGED_NAME),
                "error": ElementProperty(PropertyType.react, f"{{{_GuiCoreContext._SCENARIO_SELECTOR_ERROR_VAR}}}"),
                "type": ElementProperty(PropertyType.inner, __SCENARIO_ADAPTER),
                "scenario_edit": ElementProperty(
                    _GuiCoreScenarioAdapter,
                    f"{{{__CTX_VAR_NAME}.get_scenario_by_id({_GuiCoreContext._SCENARIO_SELECTOR_ID_VAR})}}",
                ),
                "on_scenario_select": ElementProperty(PropertyType.function, f"{{{__CTX_VAR_NAME}.select_scenario}}"),
            },
        ),
        "scenario": Element(
            "scenario",
            {
                "id": ElementProperty(PropertyType.string),
                "scenario": ElementProperty(_GuiCoreScenarioAdapter),
                "active": ElementProperty(PropertyType.dynamic_boolean, True),
                "expandable": ElementProperty(PropertyType.boolean, True),
                "expanded": ElementProperty(PropertyType.boolean, True),
                "show_submit": ElementProperty(PropertyType.boolean, True),
                "show_delete": ElementProperty(PropertyType.boolean, True),
                "show_config": ElementProperty(PropertyType.boolean, False),
                "show_cycle": ElementProperty(PropertyType.boolean, False),
                "show_tags": ElementProperty(PropertyType.boolean, True),
                "show_properties": ElementProperty(PropertyType.boolean, True),
                "show_sequences": ElementProperty(PropertyType.boolean, True),
                "show_submit_sequences": ElementProperty(PropertyType.boolean, True),
                "class_name": ElementProperty(PropertyType.dynamic_string),
            },
            inner_properties={
                "on_edit": ElementProperty(PropertyType.function, f"{{{__CTX_VAR_NAME}.edit_entity}}"),
                "on_submit": ElementProperty(PropertyType.function, f"{{{__CTX_VAR_NAME}.submit_entity}}"),
                "on_delete": ElementProperty(PropertyType.function, f"{{{__CTX_VAR_NAME}.crud_scenario}}"),
                "core_changed": ElementProperty(PropertyType.broadcast, _GuiCoreContext._CORE_CHANGED_NAME),
                "error": ElementProperty(PropertyType.react, f"{{{_GuiCoreContext._SCENARIO_VIZ_ERROR_VAR}}}"),
            },
        ),
        "scenario_dag": Element(
            "scenario",
            {
                "id": ElementProperty(PropertyType.string),
                "scenario": ElementProperty(_GuiCoreScenarioDagAdapter),
                "render": ElementProperty(PropertyType.dynamic_boolean, True),
                "show_toolbar": ElementProperty(PropertyType.boolean, True),
                "width": ElementProperty(PropertyType.string),
                "height": ElementProperty(PropertyType.string),
                "class_name": ElementProperty(PropertyType.dynamic_string),
            },
            inner_properties={
                "core_changed": ElementProperty(PropertyType.broadcast, _GuiCoreContext._CORE_CHANGED_NAME),
            },
        ),
        "data_node_selector": Element(
            "value",
            {
                "id": ElementProperty(PropertyType.string),
                "display_cycles": ElementProperty(PropertyType.boolean, True),
                "show_primary_flag": ElementProperty(PropertyType.boolean, True),
                "value": ElementProperty(PropertyType.lov_value),
                "on_change": ElementProperty(PropertyType.function),
                "height": ElementProperty(PropertyType.string, "50vh"),
                "class_name": ElementProperty(PropertyType.dynamic_string),
                "show_pins": ElementProperty(PropertyType.boolean, True),
            },
            inner_properties={
                "datanodes": ElementProperty(PropertyType.lov, f"{{{__CTX_VAR_NAME}.get_datanodes_tree()}}"),
                "core_changed": ElementProperty(PropertyType.broadcast, _GuiCoreContext._CORE_CHANGED_NAME),
                "type": ElementProperty(PropertyType.inner, __DATANODE_ADAPTER),
            },
        ),
        "data_node": Element(
            _GuiCoreContext._DATANODE_VIZ_DATA_NODE_PROP,
            {
                "id": ElementProperty(PropertyType.string),
                _GuiCoreContext._DATANODE_VIZ_DATA_NODE_PROP: ElementProperty(_GuiCoreDatanodeAdapter),
                "active": ElementProperty(PropertyType.dynamic_boolean, True),
                "expandable": ElementProperty(PropertyType.boolean, True),
                "expanded": ElementProperty(PropertyType.boolean, True),
                "show_config": ElementProperty(PropertyType.boolean, False),
                "show_owner": ElementProperty(PropertyType.boolean, True),
                "show_edit_date": ElementProperty(PropertyType.boolean, False),
                "show_expiration_date": ElementProperty(PropertyType.boolean, False),
                "show_properties": ElementProperty(PropertyType.boolean, True),
                "show_history": ElementProperty(PropertyType.boolean, True),
                "show_data": ElementProperty(PropertyType.boolean, True),
                "chart_configs": ElementProperty(PropertyType.dict),
                "class_name": ElementProperty(PropertyType.dynamic_string),
                "scenario": ElementProperty(PropertyType.lov_value),
                "width": ElementProperty(PropertyType.string),
            },
            inner_properties={
                "on_edit": ElementProperty(PropertyType.function, f"{{{__CTX_VAR_NAME}.edit_data_node}}"),
                "core_changed": ElementProperty(PropertyType.broadcast, _GuiCoreContext._CORE_CHANGED_NAME),
                "error": ElementProperty(PropertyType.react, f"{{{_GuiCoreContext._DATANODE_VIZ_ERROR_VAR}}}"),
                "scenarios": ElementProperty(
                    PropertyType.lov,
                    f"{{{__CTX_VAR_NAME}.get_scenarios_for_owner({_GuiCoreContext._DATANODE_VIZ_OWNER_ID_VAR})}}",
                ),
                "type": ElementProperty(PropertyType.inner, __SCENARIO_ADAPTER),
                "on_id_select": ElementProperty(PropertyType.function, f"{{{__CTX_VAR_NAME}.select_id}}"),
                "history": ElementProperty(
                    PropertyType.react,
                    f"{{{__CTX_VAR_NAME}.get_data_node_history("
                    + f"<tp:prop:{_GuiCoreContext._DATANODE_VIZ_DATA_NODE_PROP}>, "
                    + f"{_GuiCoreContext._DATANODE_VIZ_HISTORY_ID_VAR})}}",
                ),
                "data": ElementProperty(
                    PropertyType.react,
                    f"{{{__CTX_VAR_NAME}.get_data_node_data(<tp:prop:{_GuiCoreContext._DATANODE_VIZ_DATA_NODE_PROP}>,"
                    + f" {_GuiCoreContext._DATANODE_VIZ_DATA_ID_VAR})}}",
                ),
                "tabular_data": ElementProperty(
                    PropertyType.data,
                    f"{{{__CTX_VAR_NAME}.get_data_node_tabular_data("
                    + f"<tp:prop:{_GuiCoreContext._DATANODE_VIZ_DATA_NODE_PROP}>, "
                    + f"{_GuiCoreContext._DATANODE_VIZ_DATA_ID_VAR})}}",
                ),
                "tabular_columns": ElementProperty(
                    PropertyType.dynamic_string,
                    f"{{{__CTX_VAR_NAME}.get_data_node_tabular_columns("
                    + f"<tp:prop:{_GuiCoreContext._DATANODE_VIZ_DATA_NODE_PROP}>, "
                    + f"{_GuiCoreContext._DATANODE_VIZ_DATA_ID_VAR})}}",
                ),
                "chart_config": ElementProperty(
                    PropertyType.dynamic_string,
                    f"{{{__CTX_VAR_NAME}.get_data_node_chart_config("
                    + f"<tp:prop:{_GuiCoreContext._DATANODE_VIZ_DATA_NODE_PROP}>, "
                    + f"{_GuiCoreContext._DATANODE_VIZ_DATA_CHART_ID_VAR})}}",
                ),
                "on_data_value": ElementProperty(PropertyType.function, f"{{{__CTX_VAR_NAME}.update_data}}"),
                "on_tabular_data_edit": ElementProperty(
                    PropertyType.function, f"{{{__CTX_VAR_NAME}.tabular_data_edit}}"
                ),
            },
        ),
        "job_selector": Element(
            "value",
            {
                "id": ElementProperty(PropertyType.string),
                "class_name": ElementProperty(PropertyType.dynamic_string),
                "value": ElementProperty(PropertyType.lov_value),
                "show_job_id": ElementProperty(PropertyType.boolean, True),
                "show_entity_label": ElementProperty(PropertyType.boolean, True),
                "show_entity_id": ElementProperty(PropertyType.boolean, False),
                "show_submit_id": ElementProperty(PropertyType.boolean, False),
                "show_date": ElementProperty(PropertyType.boolean, True),
                "show_cancel": ElementProperty(PropertyType.boolean, True),
                "show_delete": ElementProperty(PropertyType.boolean, True),
                "on_change": ElementProperty(PropertyType.function),
                "height": ElementProperty(PropertyType.string, "50vh"),
            },
            inner_properties={
                "jobs": ElementProperty(PropertyType.lov, f"{{{__CTX_VAR_NAME}.get_jobs_list()}}"),
                "core_changed": ElementProperty(PropertyType.broadcast, _GuiCoreContext._CORE_CHANGED_NAME),
                "type": ElementProperty(PropertyType.inner, __JOB_ADAPTER),
                "on_job_action": ElementProperty(PropertyType.function, f"{{{__CTX_VAR_NAME}.act_on_jobs}}"),
                "error": ElementProperty(PropertyType.dynamic_string, f"{{{_GuiCoreContext._JOB_SELECTOR_ERROR_VAR}}}"),
            },
        ),
    }

    def get_name(self) -> str:
        return _GuiCore.__LIB_NAME

    def get_elements(self) -> t.Dict[str, Element]:
        return _GuiCore.__elts

    def get_scripts(self) -> t.List[str]:
        return ["lib/taipy-gui-core.js"]

    def on_init(self, gui: Gui) -> t.Optional[t.Tuple[str, t.Any]]:
        gui._get_default_locals_bind().update(
            {
                _GuiCoreContext._SCENARIO_SELECTOR_ERROR_VAR: "",
                _GuiCoreContext._SCENARIO_SELECTOR_ID_VAR: "",
                _GuiCoreContext._SCENARIO_VIZ_ERROR_VAR: "",
                _GuiCoreContext._JOB_SELECTOR_ERROR_VAR: "",
                _GuiCoreContext._DATANODE_VIZ_ERROR_VAR: "",
                _GuiCoreContext._DATANODE_VIZ_OWNER_ID_VAR: "",
                _GuiCoreContext._DATANODE_VIZ_HISTORY_ID_VAR: "",
                _GuiCoreContext._DATANODE_VIZ_DATA_ID_VAR: "",
                _GuiCoreContext._DATANODE_VIZ_DATA_CHART_ID_VAR: "",
            }
        )
        ctx = _GuiCoreContext(gui)
        gui._add_adapter_for_type(_GuiCore.__SCENARIO_ADAPTER, ctx.scenario_adapter)
        gui._add_adapter_for_type(_GuiCore.__DATANODE_ADAPTER, ctx.data_node_adapter)
        gui._add_adapter_for_type(_GuiCore.__JOB_ADAPTER, ctx.job_adapter)
        return _GuiCore.__CTX_VAR_NAME, ctx

    def on_user_init(self, state: State):
        for var in [
            _GuiCoreContext._SCENARIO_SELECTOR_ERROR_VAR,
            _GuiCoreContext._SCENARIO_SELECTOR_ID_VAR,
            _GuiCoreContext._SCENARIO_VIZ_ERROR_VAR,
            _GuiCoreContext._JOB_SELECTOR_ERROR_VAR,
            _GuiCoreContext._DATANODE_VIZ_ERROR_VAR,
            _GuiCoreContext._DATANODE_VIZ_OWNER_ID_VAR,
            _GuiCoreContext._DATANODE_VIZ_HISTORY_ID_VAR,
            _GuiCoreContext._DATANODE_VIZ_DATA_ID_VAR,
            _GuiCoreContext._DATANODE_VIZ_DATA_CHART_ID_VAR,
        ]:
            state._add_attribute(var, "")

    def get_version(self) -> str:
        if not hasattr(self, "version"):
            self.version = _get_version() + str(datetime.now().timestamp())
        return self.version
