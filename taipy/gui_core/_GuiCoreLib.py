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

import typing as t
from datetime import datetime

from taipy.core import Cycle, DataNode, Job, Scenario, Sequence, Task
from taipy.gui import Gui
from taipy.gui.extension import Element, ElementLibrary, ElementProperty, PropertyType

from ..version import _get_version
from ._adapters import (
    _GuiCoreDatanodeAdapter,
    _GuiCoreDatanodeFilter,
    _GuiCoreDatanodeSort,
    _GuiCoreDoNotUpdate,
    _GuiCoreScenarioAdapter,
    _GuiCoreScenarioDagAdapter,
    _GuiCoreScenarioFilter,
    _GuiCoreScenarioSort,
)
from ._context import _GuiCoreContext

Scenario.__bases__ += (_GuiCoreDoNotUpdate,)
Sequence.__bases__ += (_GuiCoreDoNotUpdate,)
DataNode.__bases__ += (_GuiCoreDoNotUpdate,)
Cycle.__bases__ += (_GuiCoreDoNotUpdate,)
Job.__bases__ += (_GuiCoreDoNotUpdate,)
Task.__bases__ += (_GuiCoreDoNotUpdate,)


class _GuiCore(ElementLibrary):
    __LIB_NAME = "taipy_gui_core"
    __CTX_VAR_NAME = f"__{__LIB_NAME}_Ctx"
    __SCENARIO_ADAPTER = "tgc_scenario"
    __DATANODE_ADAPTER = "tgc_datanode"
    __JOB_ADAPTER = "tgc_job"

    __SCENARIO_SELECTOR_ERROR_VAR = "__tpgc_sc_error"
    __SCENARIO_SELECTOR_ID_VAR = "__tpgc_sc_id"
    __SCENARIO_SELECTOR_FILTER_VAR = "__tpgc_sc_filter"
    __SCENARIO_SELECTOR_SORT_VAR = "__tpgc_sc_sort"
    __SCENARIO_VIZ_ERROR_VAR = "__tpgc_sv_error"
    __JOB_SELECTOR_ERROR_VAR = "__tpgc_js_error"
    __JOB_DETAIL_ID_VAR = "__tpgc_jd_id"
    __DATANODE_VIZ_ERROR_VAR = "__tpgc_dv_error"
    __DATANODE_VIZ_OWNER_ID_VAR = "__tpgc_dv_owner_id"
    __DATANODE_VIZ_HISTORY_ID_VAR = "__tpgc_dv_history_id"
    __DATANODE_VIZ_PROPERTIES_ID_VAR = "__tpgc_dv_properties_id"
    __DATANODE_VIZ_DATA_ID_VAR = "__tpgc_dv_data_id"
    __DATANODE_VIZ_DATA_CHART_ID_VAR = "__tpgc_dv_data_chart_id"
    __DATANODE_VIZ_DATA_NODE_PROP = "data_node"
    __DATANODE_SEL_SCENARIO_PROP = "scenario"
    __SEL_SCENARIOS_PROP = "scenarios"
    __SEL_DATANODES_PROP = "datanodes"
    __DATANODE_SELECTOR_FILTER_VAR = "__tpgc_dn_filter"
    __DATANODE_SELECTOR_SORT_VAR = "__tpgc_dn_sort"
    __DATANODE_SELECTOR_ERROR_VAR = "__tpgc_dn_error"

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
                "show_dialog": ElementProperty(PropertyType.boolean, True),
                __SEL_SCENARIOS_PROP: ElementProperty(PropertyType.dynamic_list),
                "multiple": ElementProperty(PropertyType.boolean, False),
                "filter": ElementProperty(_GuiCoreScenarioFilter, "*"),
                "sort": ElementProperty(_GuiCoreScenarioSort, "*"),
                "show_search": ElementProperty(PropertyType.boolean, True),
            },
            inner_properties={
                "inner_scenarios": ElementProperty(
                    PropertyType.lov_no_default,
                    f"{{{__CTX_VAR_NAME}.get_scenarios(<tp:prop:{__SEL_SCENARIOS_PROP}>, "
                    + f"{__SCENARIO_SELECTOR_FILTER_VAR}<tp:uniq:sc>, "
                    + f"{__SCENARIO_SELECTOR_SORT_VAR}<tp:uniq:sc>)}}",
                ),
                "on_scenario_crud": ElementProperty(PropertyType.function, f"{{{__CTX_VAR_NAME}.crud_scenario}}"),
                "configs": ElementProperty(PropertyType.react, f"{{{__CTX_VAR_NAME}.get_scenario_configs()}}"),
                "core_changed": ElementProperty(PropertyType.broadcast, _GuiCoreContext._CORE_CHANGED_NAME),
                "error": ElementProperty(PropertyType.react, f"{{{__SCENARIO_SELECTOR_ERROR_VAR}<tp:uniq:sc>}}"),
                "type": ElementProperty(PropertyType.inner, __SCENARIO_ADAPTER),
                "scenario_edit": ElementProperty(
                    _GuiCoreScenarioAdapter,
                    f"{{{__CTX_VAR_NAME}.get_scenario_by_id({__SCENARIO_SELECTOR_ID_VAR}<tp:uniq:sc>)}}",
                ),
                "on_scenario_select": ElementProperty(PropertyType.function, f"{{{__CTX_VAR_NAME}.select_scenario}}"),
                "creation_not_allowed": ElementProperty(
                    PropertyType.string, f"{{{__CTX_VAR_NAME}.get_creation_reason()}}"
                ),
                "update_sc_vars": ElementProperty(
                    PropertyType.string,
                    f"filter={__SCENARIO_SELECTOR_FILTER_VAR}<tp:uniq:sc>;"
                    + f"sort={__SCENARIO_SELECTOR_SORT_VAR}<tp:uniq:sc>;"
                    + f"sc_id={__SCENARIO_SELECTOR_ID_VAR}<tp:uniq:sc>;"
                    + f"error_id={__SCENARIO_SELECTOR_ERROR_VAR}<tp:uniq:sc>",
                ),
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
                "error": ElementProperty(PropertyType.react, f"{{{__SCENARIO_VIZ_ERROR_VAR}<tp:uniq:sv>}}"),
                "update_sc_vars": ElementProperty(
                    PropertyType.string,
                    f"error_id={__SCENARIO_SELECTOR_ERROR_VAR}<tp:uniq:sv>",
                ),
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
                "on_action": ElementProperty(PropertyType.function),
            },
            inner_properties={
                "core_changed": ElementProperty(PropertyType.broadcast, _GuiCoreContext._CORE_CHANGED_NAME),
                "on_select": ElementProperty(PropertyType.function, f"{{{__CTX_VAR_NAME}.on_dag_select}}"),
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
                __DATANODE_SEL_SCENARIO_PROP: ElementProperty(PropertyType.dynamic_list),
                __SEL_DATANODES_PROP: ElementProperty(PropertyType.dynamic_list),
                "multiple": ElementProperty(PropertyType.boolean, False),
                "filter": ElementProperty(_GuiCoreDatanodeFilter, "*"),
                "sort": ElementProperty(_GuiCoreDatanodeSort, "*"),
                "show_search": ElementProperty(PropertyType.boolean, True),
            },
            inner_properties={
                "inner_datanodes": ElementProperty(
                    PropertyType.lov_no_default,
                    f"{{{__CTX_VAR_NAME}.get_datanodes_tree(<tp:prop:{__DATANODE_SEL_SCENARIO_PROP}>, "
                    + f"<tp:prop:{__SEL_DATANODES_PROP}>, "
                    + f"{__DATANODE_SELECTOR_FILTER_VAR}<tp:uniq:dns>, "
                    + f"{__DATANODE_SELECTOR_SORT_VAR}<tp:uniq:dns>)}}",
                ),
                "core_changed": ElementProperty(PropertyType.broadcast, _GuiCoreContext._CORE_CHANGED_NAME),
                "type": ElementProperty(PropertyType.inner, __DATANODE_ADAPTER),
                "error": ElementProperty(PropertyType.react, f"{{{__DATANODE_SELECTOR_ERROR_VAR}<tp:uniq:dns>}}"),
                "update_dn_vars": ElementProperty(
                    PropertyType.string,
                    f"filter={__DATANODE_SELECTOR_FILTER_VAR}<tp:uniq:dns>;"
                    + f"sort={__DATANODE_SELECTOR_SORT_VAR}<tp:uniq:dns>;"
                    + f"error_id={__DATANODE_SELECTOR_ERROR_VAR}<tp:uniq:dns>",
                ),
            },
        ),
        "data_node": Element(
            __DATANODE_VIZ_DATA_NODE_PROP,
            {
                "id": ElementProperty(PropertyType.string),
                __DATANODE_VIZ_DATA_NODE_PROP: ElementProperty(_GuiCoreDatanodeAdapter),
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
                "scenario": ElementProperty(PropertyType.lov_value, "optional"),
                "width": ElementProperty(PropertyType.string),
                "file_download": ElementProperty(PropertyType.boolean, False),
                "file_upload": ElementProperty(PropertyType.boolean, False),
                "upload_check": ElementProperty(PropertyType.function),
                "show_owner_label": ElementProperty(PropertyType.boolean, False),
            },
            inner_properties={
                "on_edit": ElementProperty(PropertyType.function, f"{{{__CTX_VAR_NAME}.edit_data_node}}"),
                "core_changed": ElementProperty(PropertyType.broadcast, _GuiCoreContext._CORE_CHANGED_NAME),
                "error": ElementProperty(PropertyType.react, f"{{{__DATANODE_VIZ_ERROR_VAR}<tp:uniq:dn>}}"),
                "scenarios": ElementProperty(
                    PropertyType.lov,
                    f"{{{__CTX_VAR_NAME}.get_scenarios_for_owner({__DATANODE_VIZ_OWNER_ID_VAR}<tp:uniq:dn>)}}",
                ),
                "type": ElementProperty(PropertyType.inner, __SCENARIO_ADAPTER),
                "dn_properties": ElementProperty(
                    PropertyType.react,
                    f"{{{__CTX_VAR_NAME}.get_data_node_properties("
                    + f"{__DATANODE_VIZ_PROPERTIES_ID_VAR}<tp:uniq:dn>)}}",
                ),
                "history": ElementProperty(
                    PropertyType.react,
                    f"{{{__CTX_VAR_NAME}.get_data_node_history(" + f"{__DATANODE_VIZ_HISTORY_ID_VAR}<tp:uniq:dn>)}}",
                ),
                "tabular_data": ElementProperty(
                    PropertyType.data,
                    f"{{{__CTX_VAR_NAME}.get_data_node_tabular_data(" + f"{__DATANODE_VIZ_DATA_ID_VAR}<tp:uniq:dn>)}}",
                ),
                "tabular_columns": ElementProperty(
                    PropertyType.dynamic_string,
                    f"{{{__CTX_VAR_NAME}.get_data_node_tabular_columns("
                    + f"{__DATANODE_VIZ_DATA_ID_VAR}<tp:uniq:dn>)}}",
                    with_update=True,
                ),
                "chart_config": ElementProperty(
                    PropertyType.dynamic_string,
                    f"{{{__CTX_VAR_NAME}.get_data_node_chart_config("
                    + f"{__DATANODE_VIZ_DATA_CHART_ID_VAR}<tp:uniq:dn>)}}",
                    with_update=True,
                ),
                "on_data_value": ElementProperty(PropertyType.function, f"{{{__CTX_VAR_NAME}.update_data}}"),
                "on_tabular_data_edit": ElementProperty(
                    PropertyType.function, f"{{{__CTX_VAR_NAME}.tabular_data_edit}}"
                ),
                "on_lock": ElementProperty(PropertyType.function, f"{{{__CTX_VAR_NAME}.lock_datanode_for_edit}}"),
                "on_file_action": ElementProperty(PropertyType.function, f"{{{__CTX_VAR_NAME}.on_file_action}}"),
                "update_dn_vars": ElementProperty(
                    PropertyType.string,
                    f"data_id={__DATANODE_VIZ_DATA_ID_VAR}<tp:uniq:dn>;"
                    + f"history_id={__DATANODE_VIZ_HISTORY_ID_VAR}<tp:uniq:dn>;"
                    + f"owner_id={__DATANODE_VIZ_OWNER_ID_VAR}<tp:uniq:dn>;"
                    + f"chart_id={__DATANODE_VIZ_DATA_CHART_ID_VAR}<tp:uniq:dn>;"
                    + f"properties_id={__DATANODE_VIZ_PROPERTIES_ID_VAR}<tp:uniq:dn>;"
                    + f"error_id={__DATANODE_VIZ_ERROR_VAR}<tp:uniq:dn>",
                ),
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
                "on_details": ElementProperty(PropertyType.function),
                "height": ElementProperty(PropertyType.string, "50vh"),
            },
            inner_properties={
                "jobs": ElementProperty(PropertyType.lov, f"{{{__CTX_VAR_NAME}.get_jobs_list()}}"),
                "core_changed": ElementProperty(PropertyType.broadcast, _GuiCoreContext._CORE_CHANGED_NAME),
                "type": ElementProperty(PropertyType.inner, __JOB_ADAPTER),
                "on_job_action": ElementProperty(PropertyType.function, f"{{{__CTX_VAR_NAME}.act_on_jobs}}"),
                "error": ElementProperty(PropertyType.dynamic_string, f"{{{__JOB_SELECTOR_ERROR_VAR}<tp:uniq:jb>}}"),
                "details": ElementProperty(
                    PropertyType.react,
                    f"{{{__CTX_VAR_NAME}.get_job_details(" + f"{__JOB_DETAIL_ID_VAR}<tp:uniq:jb>)}}",
                ),
                "update_jb_vars": ElementProperty(
                    PropertyType.string,
                    f"error_id={__JOB_SELECTOR_ERROR_VAR}<tp:uniq:jb>;"
                    + f"detail_id={__JOB_DETAIL_ID_VAR}<tp:uniq:jb>;",
                ),
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

    def get_version(self) -> str:
        if not hasattr(self, "version"):
            self.version = _get_version()
            if "dev" in self.version:
                self.version += str(datetime.now().timestamp())
        return self.version
