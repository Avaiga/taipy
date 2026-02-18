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

from taipy import Gui, Sequence, SequenceId
from taipy.core.notification import Event, EventEntityType, EventOperation
from taipy.gui_core._context import _GuiCoreContext


class TestGuiCoreContextProcessSequenceEvent:

    @pytest.mark.parametrize("operation, sequence_is_valid", [(EventOperation.CREATION, True),
                                                              (EventOperation.CREATION, False),
                                                              (EventOperation.UPDATE, True),
                                                              (EventOperation.UPDATE, False),
                                                              (EventOperation.SUBMISSION, True),
                                                              (EventOperation.SUBMISSION, False),
                                                              ])
    def test_sequence_event(self, operation, sequence_is_valid):
        seq_id = "sequence_id"
        seq_parent_ids = {"a_scenario_id", "s_id"}
        sequence = Sequence({}, [], SequenceId(seq_id), parent_ids=seq_parent_ids)
        event = Event(entity_type=EventEntityType.SEQUENCE,
                      operation=operation,
                      entity_id=seq_id)
        with (
            patch("taipy.gui.gui.Gui._broadcast") as mock_broadcast,
            patch("taipy.gui_core._context.is_readable") as mock_is_readable,
            patch("taipy.gui_core._context.core_get") as mock_core_get,
            patch("taipy.gui.gui.Gui._get_authorization") as mock_get_auth
        ):
            mock_core_get.return_value = sequence
            mock_is_readable.return_value = sequence_is_valid
            gui_core_context = _GuiCoreContext(Gui())
            gui_core_context.process_event(event=event)

            mock_get_auth.assert_called_with(system=True)
            if sequence_is_valid:
                mock_broadcast.assert_called_once_with("core_changed", {"scenario": list(seq_parent_ids)}, None)
            else:
                mock_broadcast.assert_not_called()

    @pytest.mark.parametrize("sequence_is_valid", [True, False])
    def test_sequence_deletion(self, sequence_is_valid):
        event = Event(entity_type=EventEntityType.SEQUENCE,
                      operation=EventOperation.DELETION,
                      entity_id="sequence_id")
        with (
            patch("taipy.gui.gui.Gui._broadcast") as mock_broadcast,
            patch("taipy.gui_core._context.is_readable") as mock_is_readable,
            patch("taipy.gui.gui.Gui._get_authorization") as mock_get_auth
        ):
            mock_is_readable.return_value = sequence_is_valid
            gui_core_context = _GuiCoreContext(Gui())
            gui_core_context.process_event(event=event)

            mock_get_auth.assert_called_with(system=True)
            mock_broadcast.assert_not_called()

    @pytest.mark.parametrize("operation", [EventOperation.CREATION, EventOperation.UPDATE, EventOperation.SUBMISSION])
    def test_sequence_without_parent_ids(self, operation):
        seq_id = "sequence_id"
        seq_parent_ids = set()
        sequence = Sequence({}, [], SequenceId(seq_id), parent_ids=seq_parent_ids)
        event = Event(entity_type=EventEntityType.SEQUENCE,
                      operation=operation,
                      entity_id=seq_id)
        with (
            patch("taipy.gui.gui.Gui._broadcast") as mock_broadcast,
            patch("taipy.gui_core._context.is_readable") as mock_is_readable,
            patch("taipy.gui_core._context.core_get") as mock_core_get,
            patch("taipy.gui.gui.Gui._get_authorization") as mock_get_auth
        ):
            mock_core_get.return_value = sequence
            mock_is_readable.return_value = True
            gui_core_context = _GuiCoreContext(Gui())
            gui_core_context.process_event(event=event)

            mock_get_auth.assert_called_with(system=True)
            mock_broadcast.assert_not_called()
