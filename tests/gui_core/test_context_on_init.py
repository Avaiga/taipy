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


class TestGuiCoreContext_on_init:
    def test_on_init(self):
        gui_core_context = _GuiCoreContext(Mock())
        mock_state = Mock()
        gui_core_context._auth_listener = Mock(gui_core_context._auth_listener)
        gui_core_context.on_user_init(mock_state)
        gui_core_context._auth_listener.assert_not_called()

