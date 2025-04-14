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


class TestGuiCoreContextProcessJobEvent:

    @pytest.mark.parametrize("operation", [EventOperation.CREATION, EventOperation.UPDATE])
    def test_job_event(self, operation):
        event = Event(entity_type=EventEntityType.JOB,
                      operation=operation,
                      entity_id="whatever")
        gui_core_context = _GuiCoreContext(Gui())
        gui_core_context.jobs_list = ["job_id"]
        assert gui_core_context.jobs_list == ["job_id"]
        with patch("taipy.gui.gui.Gui._get_authorization") as mock_get_auth:
            gui_core_context.process_event(event=event)

            mock_get_auth.assert_called_once_with(system=True)
            assert gui_core_context.jobs_list is None


    def test_job_deletion(self):
        event = Event(entity_type=EventEntityType.JOB,
                      operation=EventOperation.DELETION,
                      entity_id="job_id")
        with (patch("taipy.gui.gui.Gui._broadcast") as mock_broadcast,
              patch("taipy.gui.gui.Gui._get_authorization") as mock_get_auth):
            gui_core_context = _GuiCoreContext(Gui())
            gui_core_context.process_event(event=event)

            mock_get_auth.assert_called_once_with(system=True)
            mock_broadcast.assert_called_once_with("core_changed", {"jobs": True}, None)
            assert gui_core_context.jobs_list is None

