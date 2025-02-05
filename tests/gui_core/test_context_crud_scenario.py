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
from taipy.gui.mock.mock_state import MockState
from taipy.gui_core._context import _GuiCoreContext

scenario_a = Scenario("scenario_a_config_id", None, {"a_prop": "a"})
scenario_b = Scenario("scenario_b_config_id", None, {"a_prop": "b"})
scenarios: t.List[t.Union[t.List, Scenario, None]] = [scenario_a, scenario_b]


datanode_a = PickleDataNode("datanode_a_config_id", Scope.SCENARIO)
datanode_b = PickleDataNode("datanode_b_config_id", Scope.SCENARIO)
datanodes: t.List[t.Union[t.List, DataNode, None]] = [datanode_a, datanode_b]


def mock_core_get(entity_id):
    if entity_id == datanode_a.id:
        return datanode_a
    if entity_id == datanode_b.id:
        return datanode_b
    return None

def mock_is_true(entity_id):
    return True

class TestGuiCoreContext_crud_scenario:
    def test_crud_scenario_delete(self):
        gui_core_context = _GuiCoreContext(Mock())
        state = MockState(Mock())

        mock_core_delete = Mock()

        with (
            patch("taipy.gui_core._context.core_get", side_effect=mock_core_get),
            patch("taipy.gui_core._context.is_deletable", side_effect=mock_is_true),
            patch("taipy.gui_core._context.core_delete", side_effect=mock_core_delete)
        ):
            gui_core_context.crud_scenario(
                state,
                "id",
                t.cast(dict, {"args": [None, None, None, True, True, {"id": "a_scenario_id"}], "error_id": "error_id"}),
            )
            mock_core_delete.assert_called_once()
