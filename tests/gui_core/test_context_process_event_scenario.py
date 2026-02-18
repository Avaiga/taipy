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
from unittest.mock import patch

import pytest

from taipy import Gui
from taipy.core.notification import Event, EventEntityType, EventOperation
from taipy.gui_core._context import _GuiCoreContext


class TestGuiCoreContextProcessScenarioEvent:

    @pytest.mark.parametrize("operation, scenario_is_valid", [(EventOperation.CREATION, True),
                                                              (EventOperation.CREATION, False),
                                                              (EventOperation.UPDATE, True),
                                                              (EventOperation.UPDATE, False),
                                                              (EventOperation.SUBMISSION, True),
                                                              (EventOperation.SUBMISSION, False),
                                                              ])
    def test_scenario_event(self, operation, scenario_is_valid):
        scenario_id = "scenario_id"
        event = Event(entity_type=EventEntityType.SCENARIO,
                      operation=operation,
                      entity_id=scenario_id)
        with (
            patch("taipy.gui.gui.Gui._broadcast") as mock_broadcast,
            patch("taipy.gui_core._context.is_readable") as mock_is_readable,
            patch("taipy.gui.gui.Gui._get_authorization") as mock_get_auth
        ):
            mock_is_readable.return_value = scenario_is_valid
            gui_core_context = _GuiCoreContext(Gui())
            gui_core_context.process_event(event=event)

            mock_get_auth.assert_called_with(system=True)
            if scenario_is_valid:
                mock_broadcast.assert_called_once_with("core_changed", {"scenario": scenario_id}, None)
            else:
                mock_broadcast.assert_called_once_with("core_changed", {"scenario": True}, None)

    @pytest.mark.parametrize("scenario_is_valid", [True, False])
    def test_scenario_deletion(self, scenario_is_valid):
        event = Event(entity_type=EventEntityType.SCENARIO,
                      operation=EventOperation.DELETION,
                      entity_id="scenario_id")
        with (
            patch("taipy.gui.gui.Gui._broadcast") as mock_broadcast,
            patch("taipy.gui_core._context.is_readable") as mock_is_readable,
            patch("taipy.gui.gui.Gui._get_authorization") as mock_get_auth
        ):
            mock_is_readable.return_value = scenario_is_valid
            gui_core_context = _GuiCoreContext(Gui())
            gui_core_context.process_event(event=event)

            mock_get_auth.assert_called_with(system=True)
            mock_broadcast.assert_called_once_with("core_changed", {"scenario": "scenario_id"}, None)

