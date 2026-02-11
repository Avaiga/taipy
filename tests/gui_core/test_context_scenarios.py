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
from unittest.mock import Mock

from taipy.core import Cycle, Scenario
from taipy.gui_core._context import _GuiCoreContext

scenario_a = Scenario("scenario_a_config_id", None, {"a_prop": "a"})
scenario_b = Scenario("scenario_b_config_id", None, {"a_prop": "b"})
scenarios: t.List[t.Union[Cycle, Scenario]] = [scenario_a, scenario_b]


class TestGuiCoreContext_scenarios:
    def test_get_scenarios_no_scenarios(self):
        gui_core_context = _GuiCoreContext(Mock())
        gui_core_context.scenario_by_cycle = {}
        new_scenarios = gui_core_context.get_scenarios(None, None, None)
        assert isinstance(new_scenarios, list)
        assert len(new_scenarios) == 0

    def test_get_scenarios_no_filter(self):
        gui_core_context = _GuiCoreContext(Mock())
        gui_core_context.scenario_by_cycle = {}
        new_scenarios = gui_core_context.get_scenarios(scenarios, None, None)
        assert len(new_scenarios) == len(scenarios)
        for new_scenario, scenario in zip(new_scenarios, scenarios):
            assert new_scenario is scenario

    def test_select_scenario(self):
        gui_core_context = _GuiCoreContext(Mock())
        mock_state = Mock()
        mock_state.assign = Mock()
        gui_core_context.select_scenario(mock_state, "", {})
        mock_state.assign.assert_not_called()
        gui_core_context.select_scenario(mock_state, "scenario_a_config_id", {"args": ["var", "value"]}) # pyright: ignore[reportArgumentType]
        mock_state.assign.assert_called_once_with("var", "value")

    def test_get_scenario_configs(self):
        gui_core_context = _GuiCoreContext(Mock())
        res = gui_core_context.get_scenario_configs()
        assert res is not None
        assert len(res) == 0
