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

from taipy.gui import Gui, State
from taipy.gui.extension import Element, ElementLibrary, ElementProperty, PropertyType

from ..version import _get_version
from ._adapters import _GuiCoreDatanodeAdapter, _GuiCoreScenarioAdapter, _GuiCoreScenarioDagAdapter
from ._context import _GuiCoreContext


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
                "on_submission_change": ElementProperty(PropertyType.function),
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
                "on_lock": ElementProperty(PropertyType.function, f"{{{__CTX_VAR_NAME}.lock_datanode_for_edit}}"),
            },
        ),
        "job_selector": Element(
            "value",
            {
                "id": ElementProperty(PropertyType.string),
                "class_name": ElementProperty(PropertyType.dynamic_string),
                "value": ElementProperty(PropertyType.lov_value),
                "show_id": ElementProperty(PropertyType.boolean, True),
                "show_submitted_label": ElementProperty(PropertyType.boolean, True),
                "show_submitted_id": ElementProperty(PropertyType.boolean, False),
                "show_submission_id": ElementProperty(PropertyType.boolean, False),
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
