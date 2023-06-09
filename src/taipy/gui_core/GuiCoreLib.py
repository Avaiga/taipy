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
from datetime import datetime

from dateutil import parser

import taipy as tp
from taipy.core import Cycle, DataNode, Pipeline, Scenario
from taipy.core.notification import CoreEventConsumerBase, EventEntityType
from taipy.core.notification.event import Event
from taipy.core.notification.notifier import Notifier
from taipy.gui import Gui, State
from taipy.gui.extension import Element, ElementLibrary, ElementProperty, PropertyType
from taipy.gui.utils import _TaipyBase

from ..version import _get_version


class _GuiCoreScenarioAdapter(_TaipyBase):
    __INNER_PROPS = ["name"]

    def get(self):
        data = super().get()
        if isinstance(data, Scenario):
            scenario = tp.get(data.id)
            if scenario:
                return [
                    scenario.id,
                    scenario.is_primary,
                    scenario.config_id,
                    scenario.creation_date,
                    scenario.get_simple_label(),
                    list(scenario.tags),
                    [(k, v) for k, v in scenario.properties.items() if k not in _GuiCoreScenarioAdapter.__INNER_PROPS],
                    [(p.id, p.get_simple_label()) for p in scenario.pipelines.values()],
                    list(scenario.properties.get("authorized_tags", set())),
                    tp.is_deletable(scenario),  # deletable
                ]
        return None

    @staticmethod
    def get_hash():
        return _TaipyBase._HOLDER_PREFIX + "Sc"


class _GuiCoreScenarioIdAdapter(_TaipyBase):
    def get(self):
        data = super().get()
        if isinstance(data, Scenario):
            scenario = tp.get(data.id)
            if scenario:
                return scenario.id
        return None

    @staticmethod
    def get_hash():
        return _TaipyBase._HOLDER_PREFIX + "ScI"


class _GuiCoreScenarioDagAdapter(_TaipyBase):
    @staticmethod
    def get_entity_type(node: t.Any):
        return DataNode.__name__ if isinstance(node.entity, DataNode) else node.type

    def get(self):
        data = super().get()
        if isinstance(data, Scenario):
            scenario = tp.get(data.id)
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
                    data.get_label(),
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
    _CORE_CHANGED_NAME = "core_changed"
    _SCENARIO_SELECTOR_ERROR_VAR = "gui_core_sc_error"
    _SCENARIO_SELECTOR_ID_VAR = "gui_core_sc_id"
    _SCENARIO_VIZ_ERROR_VAR = "gui_core_sv_error"

    def __init__(self, gui: Gui) -> None:
        self.gui = gui
        self.cycles_scenarios: t.Optional[t.List[t.Union[Cycle, Scenario]]] = None
        self.scenario_configs: t.Optional[t.List[t.Tuple[str, str]]] = None
        # register to taipy core notification
        reg_id, reg_queue = Notifier.register()
        super().__init__(reg_id, reg_queue)
        self.start()

    def process_event(self, event: Event):
        if event.entity_type == EventEntityType.SCENARIO:
            self.cycles_scenarios = None
            scenario = tp.get(event.entity_id) if event.operation.value != 3 else None
            self.gui.broadcast(
                _GuiCoreContext._CORE_CHANGED_NAME,
                {"scenario": event.entity_id if scenario else True},
            )
        elif event.entity_type == EventEntityType.PIPELINE and event.entity_id:  # TODO import EventOperation
            pipeline = tp.get(event.entity_id) if event.operation.value != 3 else None
            if pipeline:
                if hasattr(pipeline, "parent_ids") and pipeline.parent_ids:
                    self.gui.broadcast(
                        _GuiCoreContext._CORE_CHANGED_NAME, {"scenario": [x for x in pipeline.parent_ids]}
                    )

    @staticmethod
    def scenario_adapter(data):
        if hasattr(data, "id") and tp.get(data.id) is not None:
            if isinstance(data, Cycle):
                return (data.id, data.name, tp.get_scenarios(data), 0, False)
            elif isinstance(data, Scenario):
                return (data.id, data.name, None, 1, data.is_primary)
        return None

    def get_scenarios(self):
        if self.cycles_scenarios is None:
            self.cycles_scenarios = []
            for cycle, scenarios in tp.get_cycles_scenarios().items():
                if cycle is None:
                    self.cycles_scenarios.extend(scenarios)
                else:
                    self.cycles_scenarios.append(cycle)
        return self.cycles_scenarios

    def select_scenario(self, state: State, id: str, action: str, payload: t.Dict[str, str]):
        args = payload.get("args")
        if args is None or not isinstance(args, list) or len(args) == 0:
            return
        state.assign(_GuiCoreContext._SCENARIO_SELECTOR_ID_VAR, args[0])

    def get_scenario_by_id(self, id: str) -> t.Optional[Scenario]:
        if not id:
            return None
        try:
            return tp.get(id)
        except Exception:
            return None

    def get_scenario_configs(self):
        if self.scenario_configs is None:
            configs = tp.Config.scenarios
            if isinstance(configs, dict):
                self.scenario_configs = [(id, f"{c.id}") for id, c in configs.items()]
        return self.scenario_configs

    def crud_scenario(self, state: State, id: str, action: str, payload: t.Dict[str, str]):
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
                    tp.delete(scenario_id)
                except Exception as e:
                    state.assign(_GuiCoreContext._SCENARIO_SELECTOR_ERROR_VAR, f"Error deleting Scenario. {e}")
            else:
                scenario = tp.get(scenario_id)
        else:
            config_id = data.get(_GuiCoreContext.__PROP_SCENARIO_CONFIG_ID)
            scenario_config = tp.Config.scenarios.get(config_id)
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
                scenario = tp.create_scenario(scenario_config, date, name)
            except Exception as e:
                state.assign(_GuiCoreContext._SCENARIO_SELECTOR_ERROR_VAR, f"Error creating Scenario. {e}")
        if scenario:
            with scenario as sc:
                sc._properties[_GuiCoreContext.__PROP_ENTITY_NAME] = name
                if props := data.get("properties"):
                    try:
                        for prop in props:
                            key = prop.get("key")
                            if key and key not in _GuiCoreContext.__SCENARIO_PROPS:
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
        entity: t.Union[Scenario, Pipeline] = tp.get(entity_id)
        if entity:
            with entity as ent:
                try:
                    if isinstance(entity, Scenario):
                        primary = data.get(_GuiCoreContext.__PROP_SCENARIO_PRIMARY)
                        if primary is True:
                            tp.set_primary(ent)
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

    def submit_entity(self, state: State, id: str, action: str, payload: t.Dict[str, str]):
        args = payload.get("args")
        if args is None or not isinstance(args, list) or len(args) < 1 or not isinstance(args[0], dict):
            return
        data = args[0]
        entity_id = data.get(_GuiCoreContext.__PROP_ENTITY_ID)
        entity = tp.get(entity_id)
        if entity:
            try:
                tp.submit(entity)
                state.assign(_GuiCoreContext._SCENARIO_VIZ_ERROR_VAR, "")
            except Exception as e:
                state.assign(_GuiCoreContext._SCENARIO_VIZ_ERROR_VAR, f"Error submitting entity. {e}")

    def broadcast_core_changed(self):
        self.gui.broadcast(_GuiCoreContext._CORE_CHANGED_NAME, "")


class GuiCore(ElementLibrary):
    __LIB_NAME = "taipy_gui_core"
    __CTX_VAR_NAME = f"__{__LIB_NAME}_Ctx"

    __elts = {
        "scenario_selector": Element(
            "value",
            {
                "show_add_button": ElementProperty(PropertyType.dynamic_boolean, True),
                "display_cycles": ElementProperty(PropertyType.dynamic_boolean, True),
                "show_primary_flag": ElementProperty(PropertyType.dynamic_boolean, True),
                "value": ElementProperty(PropertyType.lov_value),
                "on_change": ElementProperty(PropertyType.function),
            },
            inner_properties={
                "scenarios": ElementProperty(PropertyType.lov, f"{{{__CTX_VAR_NAME}.get_scenarios()}}"),
                "on_scenario_crud": ElementProperty(PropertyType.function, f"{{{__CTX_VAR_NAME}.crud_scenario}}"),
                "configs": ElementProperty(PropertyType.react, f"{{{__CTX_VAR_NAME}.get_scenario_configs()}}"),
                "core_changed": ElementProperty(PropertyType.broadcast, _GuiCoreContext._CORE_CHANGED_NAME),
                "error": ElementProperty(PropertyType.react, f"{{{_GuiCoreContext._SCENARIO_SELECTOR_ERROR_VAR}}}"),
                "type": ElementProperty(PropertyType.inner, Scenario),
                "adapter": ElementProperty(PropertyType.inner, _GuiCoreContext.scenario_adapter),
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
                "expanded": ElementProperty(PropertyType.dynamic_boolean, False),
                "show_submit": ElementProperty(PropertyType.boolean, True),
                "show_delete": ElementProperty(PropertyType.boolean, True),
                "show_config": ElementProperty(PropertyType.boolean, False),
                "show_cycle": ElementProperty(PropertyType.boolean, False),
                "show_tags": ElementProperty(PropertyType.boolean, False),
                "show_properties": ElementProperty(PropertyType.boolean, True),
                "show_pipelines": ElementProperty(PropertyType.boolean, True),
                "show_submit_pipelines": ElementProperty(PropertyType.boolean, True),
            },
            inner_properties={
                "on_edit": ElementProperty(PropertyType.function, f"{{{__CTX_VAR_NAME}.edit_entity}}"),
                "on_submit": ElementProperty(PropertyType.function, f"{{{__CTX_VAR_NAME}.submit_entity}}"),
                "on_delete": ElementProperty(PropertyType.function, f"{{{__CTX_VAR_NAME}.crud_scenario}}"),
                "core_changed": ElementProperty(PropertyType.broadcast, _GuiCoreContext._CORE_CHANGED_NAME),
                "error": ElementProperty(PropertyType.react, f"{{{_GuiCoreContext._SCENARIO_VIZ_ERROR_VAR}}}"),
            },
        ),
        "dag": Element(
            "scenario",
            {
                "id": ElementProperty(PropertyType.string),
                "scenario": ElementProperty(_GuiCoreScenarioDagAdapter),
                "button_label": ElementProperty(PropertyType.dynamic_string),
                "show": ElementProperty(PropertyType.dynamic_boolean, True),
                "with_button": ElementProperty(PropertyType.boolean, True),
                "width": ElementProperty(PropertyType.string),
                "height": ElementProperty(PropertyType.string),
            },
            inner_properties={
                "core_changed": ElementProperty(PropertyType.broadcast, _GuiCoreContext._CORE_CHANGED_NAME),
            },
        ),
        "data_node_selector": Element(
            "val",
            {
                "val": ElementProperty(GuiCoreScenarioDagAdapter),
            },
            inner_properties={
                "scenarios": ElementProperty(PropertyType.lov, f"{{{__CTX_VAR_NAME}.get_scenarios()}}"),
                "core_changed": ElementProperty(PropertyType.broadcast, GuiCoreContext._CORE_CHANGED_NAME),
            },
        ),
    }

    def get_name(self) -> str:
        return GuiCore.__LIB_NAME

    def get_elements(self) -> t.Dict[str, Element]:
        return GuiCore.__elts

    def get_scripts(self) -> t.List[str]:
        return ["lib/taipy-gui-core.js"]

    def on_init(self, gui: Gui) -> t.Optional[t.Tuple[str, t.Any]]:
        return GuiCore.__CTX_VAR_NAME, _GuiCoreContext(gui)

    def on_user_init(self, state: State):
        for var in [
            _GuiCoreContext._SCENARIO_SELECTOR_ERROR_VAR,
            _GuiCoreContext._SCENARIO_SELECTOR_ID_VAR,
            _GuiCoreContext._SCENARIO_VIZ_ERROR_VAR,
        ]:
            state._add_attribute(var, "")

    def get_version(self) -> str:
        if not hasattr(self, "version"):
            self.version = _get_version() + str(datetime.now().timestamp())
        return self.version
