# Copyright 2021-2025 Avaiga Private Limited
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
from unittest.mock import Mock, patch

from taipy import Scope
from taipy.core import DataNode, Scenario
from taipy.core.data.pickle import PickleDataNode
from taipy.gui_core._context import _GuiCoreContext

scenario_a = Scenario("scenario_a_config_id", None, {"a_prop": "a"})
scenario_b = Scenario("scenario_b_config_id", None, {"a_prop": "b"})
scenarios: t.List[t.Union[t.List, Scenario, None]] = [scenario_a, scenario_b]


class TestGuiCoreContext_filter_scenarios:
    def test_get_filtered_scenario_list_no_filter(self):
        gui_core_context = _GuiCoreContext(Mock())
        assert gui_core_context.get_filtered_scenario_list(scenarios, None) is scenarios

    def test_get_filtered_scenario_list_a_filter(self):
        gui_core_context = _GuiCoreContext(Mock())
        res = gui_core_context.get_filtered_scenario_list(
            scenarios, [{"col": "config_id", "type": "str", "value": "_a_", "action": "contains"}]
        )
        assert len(res) == 1
        assert res[0] is scenario_a

    def test_get_filtered_scenario_list_a_filter_case(self):
        gui_core_context = _GuiCoreContext(Mock())
        res = gui_core_context.get_filtered_scenario_list(
            scenarios, [{"col": "config_id", "type": "str", "value": "_a_", "action": "contains", "matchCase": True}]
        )
        assert len(res) == 1
        assert res[0] is scenario_a

        res = gui_core_context.get_filtered_scenario_list(
            scenarios, [{"col": "config_id", "type": "str", "value": "_A_", "action": "contains", "matchCase": False}]
        )
        assert len(res) == 1
        assert res[0] is scenario_a

        res = gui_core_context.get_filtered_scenario_list(
            scenarios, [{"col": "config_id", "type": "str", "value": "_A_", "action": "contains", "matchCase": True}]
        )
        assert len(res) == 0


datanode_a = PickleDataNode("datanode_a_config_id", Scope.SCENARIO)
datanode_b = PickleDataNode("datanode_b_config_id", Scope.SCENARIO)
datanodes: t.List[t.Union[t.List, DataNode, None]] = [datanode_a, datanode_b]


def mock_core_get(entity_id):
    if entity_id == datanode_a.id:
        return datanode_a
    if entity_id == datanode_b.id:
        return datanode_b
    return None


class TestGuiCoreContext_filter_datanodes:
    def test_get_filtered_datanode_list_no_filter(self):
        gui_core_context = _GuiCoreContext(Mock())
        assert gui_core_context.get_filtered_datanode_list(datanodes, None) is datanodes

    def test_get_filtered_datanode_list_a_filter(self):
        with patch("taipy.gui_core._context.core_get", side_effect=mock_core_get):
            gui_core_context = _GuiCoreContext(Mock())
            res = gui_core_context.get_filtered_datanode_list(
                datanodes, [{"col": "config_id", "type": "str", "value": "_a_", "action": "contains"}]
            )
            assert len(res) == 1
            assert res[0] is datanode_a

    def test_get_filtered_datanode_list_a_filter_case(self):
        with patch("taipy.gui_core._context.core_get", side_effect=mock_core_get):
            gui_core_context = _GuiCoreContext(Mock())
            res = gui_core_context.get_filtered_datanode_list(
                datanodes,
                [{"col": "config_id", "type": "str", "value": "_a_", "action": "contains", "matchCase": True}],
            )
            assert len(res) == 1
            assert res[0] is datanode_a

            res = gui_core_context.get_filtered_datanode_list(
                datanodes,
                [{"col": "config_id", "type": "str", "value": "_A_", "action": "contains", "matchCase": False}],
            )
            assert len(res) == 1
            assert res[0] is datanode_a

            res = gui_core_context.get_filtered_datanode_list(
                datanodes,
                [{"col": "config_id", "type": "str", "value": "_A_", "action": "contains", "matchCase": True}],
            )
            assert len(res) == 0
