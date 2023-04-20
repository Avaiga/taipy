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

from dateutil import parser

import taipy as tp
from taipy.gui import Gui, State
from taipy.gui.extension import Element, ElementLibrary, ElementProperty, PropertyType


class GuiCoreContext:
    __PROP_SCENARIO_CONFIG_ID = "config"
    __PROP_SCENARIO_DATE = "date"
    __PROP_SCENARIO_NAME = "name"
    __SCENARIO_PROPS = (__PROP_SCENARIO_CONFIG_ID, __PROP_SCENARIO_DATE, __PROP_SCENARIO_NAME)
    _CORE_CHANGED_NAME = "core_changed"
    _ERROR_VAR = "gui_core_error"

    def __init__(self, gui: Gui) -> None:
        self.gui = gui
        self.scenarios: t.Optional[
            t.List[t.Tuple[str, str, int, bool, t.Optional[t.List[t.Tuple[str, str, int, bool, None]]]]]
        ] = None
        self.scenario_configs: t.Optional[t.List[t.Tuple[str, str]]] = None

    def __add_scenarios(self, res, scenarios):
        for scenario in scenarios:
            res.append((scenario.id, scenario.name, 1, scenario.is_primary, None))
        return res

    def get_scenarios(self):
        if self.scenarios is None:
            self.scenarios = []
            for cycle, scenarios in tp.get_cycles_scenarios().items():
                if cycle is None:
                    self.__add_scenarios(self.scenarios, scenarios)
                else:
                    self.scenarios.append((cycle.id, cycle.name, 0, False, self.__add_scenarios([], scenarios)))
        return self.scenarios

    def get_scenario_configs(self):
        if self.scenario_configs is None:
            configs = tp.Config.scenarios
            if isinstance(configs, dict):
                self.scenario_configs = [(id, f"{c.id}") for id, c in configs.items()]
        return self.scenario_configs

    def create_new_scenario(self, state: State, id: str, action: str, payload: t.Dict[str, str]):
        print(f"create_new_scenario(state, {id}, {action}, {payload}")
        args = payload.get("args")
        if args is None or not isinstance(args, list) or len(args) == 0 or not isinstance(args[0], dict):
            return
        data = args[0]
        config_id = data.get(GuiCoreContext.__PROP_SCENARIO_CONFIG_ID)
        scenario_config = tp.Config.scenarios.get(config_id)
        if scenario_config is None:
            state.assign(GuiCoreContext._ERROR_VAR, f"Invalid configuration id ({config_id})")
            return
        date_str = data.get(GuiCoreContext.__PROP_SCENARIO_DATE)
        try:
            date = parser.parse(date_str) if isinstance(date_str, str) else None
        except Exception as e:
            state.assign(GuiCoreContext._ERROR_VAR, f"Invalid date ({date_str}).{e}")
            return
        scenario = tp.create_scenario(scenario_config, date, data.get(GuiCoreContext.__PROP_SCENARIO_NAME))
        if props := data.get("properties"):
            for prop in props:
                key = prop.get("key")
                if key and key not in GuiCoreContext.__SCENARIO_PROPS:
                    scenario._properties[key] = prop.get("value")
        state.assign(GuiCoreContext._ERROR_VAR, "")

        # that should be done following the event fired by Core
        self.scenarios = None
        self.gui.broadcast(GuiCoreContext._CORE_CHANGED_NAME, {"scenario": True})

    def broadcast_core_changed(self):
        self.gui.broadcast(GuiCoreContext._CORE_CHANGED_NAME, "")


class GuiCore(ElementLibrary):
    __LIB_NAME = "taipy_gui_core"
    __CTX_VAR_NAME = f"__{__LIB_NAME}_Ctx"

    __elts = {
        "scenario_selector": Element(
            "scenario_id",
            {
                "show_add_button": ElementProperty(PropertyType.dynamic_boolean, True),
                "display_cycles": ElementProperty(PropertyType.dynamic_boolean, True),
                "show_primary_flag": ElementProperty(PropertyType.dynamic_boolean, True),
                "scenario_id": ElementProperty(PropertyType.dynamic_string),
                "scenarios": ElementProperty(PropertyType.react, f"{{{__CTX_VAR_NAME}.get_scenarios()}}"),
                "on_scenario_create": ElementProperty(
                    PropertyType.function, f"{{{__CTX_VAR_NAME}.create_new_scenario}}"
                ),
                "configs": ElementProperty(PropertyType.react, f"{{{__CTX_VAR_NAME}.get_scenario_configs()}}"),
                "core_changed": ElementProperty(PropertyType.broadcast, GuiCoreContext._CORE_CHANGED_NAME),
                "error": ElementProperty(PropertyType.react, GuiCoreContext._ERROR_VAR),
            },
        )
    }

    def get_name(self) -> str:
        return GuiCore.__LIB_NAME

    def get_elements(self) -> t.Dict[str, Element]:
        return GuiCore.__elts

    def get_scripts(self) -> t.List[str]:
        return ["lib/taipy-gui-core.js"]

    def on_init(self, gui: Gui) -> t.Optional[t.Tuple[str, t.Any]]:
        return GuiCore.__CTX_VAR_NAME, GuiCoreContext(gui)

    def on_user_init(self, state: State):
        state._add_attribute(GuiCoreContext._ERROR_VAR)
        state._gui._bind_var_val(GuiCoreContext._ERROR_VAR, "")
