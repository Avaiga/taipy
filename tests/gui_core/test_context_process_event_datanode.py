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
from collections import defaultdict
from unittest.mock import patch

import pytest

from taipy import DataNode, Gui, Scope
from taipy.core.notification import Event, EventEntityType, EventOperation
from taipy.gui_core._context import _GuiCoreContext


class TestGuiCoreContextProcessDatanodeEvent:

    @pytest.mark.parametrize("operation", [EventOperation.CREATION, EventOperation.UPDATE])
    def test_datanode_event(self, operation):
        event = Event(entity_type=EventEntityType.DATA_NODE,
                      operation=operation,
                      entity_id="whatever")
        gui_core_context = _GuiCoreContext(Gui())
        gui_core_context.data_nodes_by_owner = defaultdict(list)
        gui_core_context.data_nodes_by_owner["owner_id"] = [DataNode(config_id="cfg_id", scope=Scope.SCENARIO)]
        assert len(gui_core_context.data_nodes_by_owner) == 1

        with (patch("taipy.gui.gui.Gui._broadcast") as mock_broadcast,
              patch("taipy.gui.gui.Gui._get_authorization") as mock_get_auth):
            gui_core_context.process_event(event=event)

            mock_get_auth.assert_called_once_with(system=True)
            assert gui_core_context.data_nodes_by_owner is None
            mock_broadcast.assert_called_once_with("core_changed", {"datanode": "whatever"}, None)

    def test_datanode_deletion_event(self):
        event = Event(entity_type=EventEntityType.DATA_NODE,
                      operation=EventOperation.DELETION,
                      entity_id="whatever")
        gui_core_context = _GuiCoreContext(Gui())
        gui_core_context.data_nodes_by_owner = defaultdict(list)
        gui_core_context.data_nodes_by_owner["owner_id"] = [DataNode(config_id="cfg_id", scope=Scope.SCENARIO)]
        assert len(gui_core_context.data_nodes_by_owner) == 1

        with (patch("taipy.gui.gui.Gui._broadcast") as mock_broadcast,
              patch("taipy.gui.gui.Gui._get_authorization") as mock_get_auth):
            gui_core_context.process_event(event=event)

            mock_get_auth.assert_called_once_with(system=True)
            assert gui_core_context.data_nodes_by_owner is None
            mock_broadcast.assert_called_once_with("core_changed", {"datanode": True}, None)
