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
from collections import defaultdict
from datetime import datetime
from enum import Enum
from threading import Lock

from dateutil import parser

from taipy.config import Config
from taipy.core import Cycle, DataNode, Job, Pipeline, Scenario, cancel_job, create_scenario
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
from taipy.core.notification import CoreEventConsumerBase, EventEntityType
from taipy.core.notification.event import Event
from taipy.core.notification.notifier import Notifier
from taipy.gui import Gui, State, invoke_long_callback
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
Pipeline.__bases__ += (_GCDoNotUpdate,)
DataNode.__bases__ += (_GCDoNotUpdate,)
Job.__bases__ += (_GCDoNotUpdate,)

Config.configure_global_app(read_entity_retry=3)


class _EntityType(Enum):
    CYCLE = 0
    SCENARIO = 1
    PIPELINE = 2
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
                    scenario.creation_date,
                    scenario.get_simple_label(),
                    list(scenario.tags),
                    [(k, v) for k, v in scenario.properties.items() if k not in _GuiCoreScenarioAdapter.__INNER_PROPS],
                    [(p.id, p.get_simple_label(), is_submittable(p)) for p in scenario.pipelines.values()],
                    list(scenario.properties.get("authorized_tags", set())),
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


class _GuiCoreContext(CoreEventConsumerBase):
    __PROP_ENTITY_ID = "id"
    __PROP_SCENARIO_CONFIG_ID = "config"
    __PROP_SCENARIO_DATE = "date"
    __PROP_ENTITY_NAME = "name"
    __PROP_SCENARIO_PRIMARY = "primary"
    __PROP_SCENARIO_TAGS = "tags"
    __SCENARIO_PROPS = (__PROP_SCENARIO_CONFIG_ID, __PROP_SCENARIO_DATE, __PROP_ENTITY_NAME)
    __ACTION = "action"
    __CONTEXT = "context"
    __CREATE_ACTION = "create_action"
    _CORE_CHANGED_NAME = "core_changed"
    _SCENARIO_SELECTOR_ERROR_VAR = "gui_core_sc_error"
    _SCENARIO_SELECTOR_ID_VAR = "gui_core_sc_id"
    _SCENARIO_VIZ_ERROR_VAR = "gui_core_sv_error"
    _JOB_SELECTOR_ERROR_VAR = "gui_core_js_error"

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
        elif event.entity_type == EventEntityType.PIPELINE and event.entity_id:  # TODO import EventOperation
            pipeline = core_get(event.entity_id) if event.operation.value != 3 else None
            if pipeline:
                if hasattr(pipeline, "parent_ids") and pipeline.parent_ids:
                    self.gui.broadcast(
                        _GuiCoreContext._CORE_CHANGED_NAME, {"scenario": [x for x in pipeline.parent_ids]}
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
            if isinstance(data, Cycle):
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
            or len(args) < 4
            or not isinstance(args[0], bool)
            or not isinstance(args[1], bool)
            or not isinstance(args[2], dict)
            or not isinstance(args[3], dict)
        ):
            return
        update = args[0]
        delete = args[1]
        data = args[2]
        action_data = args[3]
        scenario = None
        name = data.get(_GuiCoreContext.__PROP_ENTITY_NAME)
        user_action = None
        module_context = action_data.get(_GuiCoreContext.__CONTEXT)
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
            config_id = data.get(_GuiCoreContext.__PROP_SCENARIO_CONFIG_ID)
            scenario_config = Config.scenarios.get(config_id)
            if scenario_config is None:
                state.assign(_GuiCoreContext._SCENARIO_SELECTOR_ERROR_VAR, f"Invalid configuration id ({config_id})")
                return
            date_str = data.get(_GuiCoreContext.__PROP_SCENARIO_DATE)
            try:
                date = parser.parse(date_str) if isinstance(date_str, str) else None
            except Exception as e:
                state.assign(_GuiCoreContext._SCENARIO_SELECTOR_ERROR_VAR, f"Invalid date ({date_str}).{e}")
                return
            try:
                scenario = create_scenario(scenario_config, date, name)
                user_action = action_data.get(_GuiCoreContext.__CREATE_ACTION)
            except Exception as e:
                state.assign(_GuiCoreContext._SCENARIO_SELECTOR_ERROR_VAR, f"Error creating Scenario. {e}")
        if scenario:
            with scenario as sc:
                sc.properties[_GuiCoreContext.__PROP_ENTITY_NAME] = name
                if props := data.get("properties"):
                    try:
                        new_keys = [prop.get("key") for prop in props]
                        for key in t.cast(dict, sc.properties).keys():
                            if key and key not in _GuiCoreContext.__SCENARIO_PROPS and key not in new_keys:
                                t.cast(dict, sc.properties).pop(key, None)
                        for prop in props:
                            key = prop.get("key")
                            if key and key not in _GuiCoreContext.__SCENARIO_PROPS:
                                sc._properties[key] = prop.get("value")
                        state.assign(_GuiCoreContext._SCENARIO_SELECTOR_ERROR_VAR, "")
                    except Exception as e:
                        state.assign(_GuiCoreContext._SCENARIO_SELECTOR_ERROR_VAR, f"Error creating Scenario. {e}")
        if user_action:
            gui: Gui = state._gui
            user_fn = gui._get_user_function(user_action)
            if callable(user_fn):
                try:
                    if module_context is not None:
                        gui._set_locals_context(module_context)
                    gui._call_function_with_state(user_fn, [scenario])
                except Exception as e:  # pragma: no cover
                    if not gui._call_on_exception(user_fn.__name__, e):
                        _warn(f"invoke_callback(): Exception raised in '{user_fn.__name__}()':\n{e}")

    def edit_entity(self, state: State, id: str, action: str, payload: t.Dict[str, str]):
        args = payload.get("args")
        if args is None or not isinstance(args, list) or len(args) < 1 or not isinstance(args[0], dict):
            return
        data = args[0]
        entity_id = data.get(_GuiCoreContext.__PROP_ENTITY_ID)
        entity: t.Union[Scenario, Pipeline] = core_get(entity_id)
        if entity:
            try:
                if isinstance(entity, Scenario):
                    primary = data.get(_GuiCoreContext.__PROP_SCENARIO_PRIMARY)
                    if primary is True:
                        set_primary(entity)
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
                            if key and key not in _GuiCoreContext.__SCENARIO_PROPS:
                                ent.properties[key] = prop.get("value")
                    deleted_props = data.get("deleted_properties")
                    if isinstance(deleted_props, (list, tuple)):
                        for prop in deleted_props:
                            key = prop.get("key")
                            if key and key not in _GuiCoreContext.__SCENARIO_PROPS:
                                ent.properties.pop(key, None)
                    state.assign(_GuiCoreContext._SCENARIO_VIZ_ERROR_VAR, "")
            except Exception as e:
                state.assign(_GuiCoreContext._SCENARIO_VIZ_ERROR_VAR, f"Error updating Scenario. {e}")

    def submit_status(
        self,
        state: State,
        status: bool,
        entity_id: str,
        user_action: t.Optional[str] = None,
        module_context: t.Optional[str] = None,
        submit_return: t.Optional[t.Union[Job, t.List[Job]]] = None,
    ):
        if user_action:
            gui: Gui = state._gui
            user_fn = gui._get_user_function(user_action)
            if callable(user_fn):
                try:
                    if module_context is not None:
                        gui._set_locals_context(module_context)
                    gui._call_function_with_state(user_fn, [status, core_get(entity_id), submit_return])
                except Exception as e:  # pragma: no cover
                    if not gui._call_on_exception(user_fn.__name__, e):
                        _warn(f"invoke_callback(): Exception raised in '{user_fn.__name__}()':\n{e}")

    def submit_entity(self, state: State, id: str, action: str, payload: t.Dict[str, str]):
        args = payload.get("args")
        if args is None or not isinstance(args, list) or len(args) < 1 or not isinstance(args[0], dict):
            return
        data = args[0]
        entity_id = data.get(_GuiCoreContext.__PROP_ENTITY_ID)
        entity = core_get(entity_id)
        if entity:
            try:
                invoke_long_callback(
                    state,
                    core_submit,
                    [entity, False, True],
                    self.submit_status,
                    [entity.id, data.get(_GuiCoreContext.__ACTION), data.get(_GuiCoreContext.__CONTEXT)],
                )
                state.assign(_GuiCoreContext._SCENARIO_VIZ_ERROR_VAR, "")
            except Exception as e:
                state.assign(_GuiCoreContext._SCENARIO_VIZ_ERROR_VAR, f"Error submitting entity. {e}")

    def get_datanodes_tree(self):
        with self.lock:
            if self.data_nodes_by_owner is None:
                self.data_nodes_by_owner = defaultdict(list)
                for dn in get_data_nodes():
                    self.data_nodes_by_owner[dn.owner_id].append(dn)
        return self.get_scenarios()

    def data_node_adapter(self, data):
        if hasattr(data, "id") and core_get(data.id) is not None:
            if isinstance(data, DataNode):
                return (data.id, data.get_simple_label(), None, _EntityType.DATANODE.value, False)
            else:
                with self.lock:
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
                            self.data_nodes_by_owner[data.id] + list(data.pipelines.values()),
                            _EntityType.SCENARIO.value,
                            data.is_primary,
                        )
                    elif isinstance(data, Pipeline):
                        if datanodes := self.data_nodes_by_owner.get(data.id):
                            return (data.id, data.get_simple_label(), datanodes, _EntityType.PIPELINE.value, False)
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
                "on_create": ElementProperty(PropertyType.function),
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
                "expanded": ElementProperty(PropertyType.boolean, False),
                "show_submit": ElementProperty(PropertyType.boolean, True),
                "show_delete": ElementProperty(PropertyType.boolean, True),
                "show_config": ElementProperty(PropertyType.boolean, False),
                "show_cycle": ElementProperty(PropertyType.boolean, False),
                "show_tags": ElementProperty(PropertyType.boolean, False),
                "show_properties": ElementProperty(PropertyType.boolean, True),
                "show_pipelines": ElementProperty(PropertyType.boolean, True),
                "show_submit_pipelines": ElementProperty(PropertyType.boolean, True),
                "class_name": ElementProperty(PropertyType.dynamic_string),
                "on_execution_end": ElementProperty(PropertyType.function),
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
        ]:
            state._add_attribute(var, "")

    def get_version(self) -> str:
        if not hasattr(self, "version"):
            self.version = _get_version() + str(datetime.now().timestamp())
        return self.version
