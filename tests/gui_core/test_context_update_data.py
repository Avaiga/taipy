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
from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from taipy import DataNode, Gui, Scope
from taipy.core.data._data_manager_factory import _DataManagerFactory
from taipy.core.data.pickle import PickleDataNode
from taipy.core.reason import Reason, ReasonCollection
from taipy.gui_core._context import _GuiCoreContext

dn = PickleDataNode("data_node_config_id", Scope.SCENARIO)


def core_get(entity_id):
    if entity_id == dn.id:
        return dn
    return None


def is_false(entity_id):
    return ReasonCollection()._add_reason(entity_id, Reason("foo"))


def is_true(entity_id):
    return True

def fails(**kwargs):
    raise Exception("Failed")


class MockState:
    def __init__(self, **kwargs) -> None:
        self.assign = kwargs.get("assign")


class TestGuiCoreContext_update_data:

    @pytest.fixture(scope="class", autouse=True)
    def set_entities(self):
        _DataManagerFactory._build_manager()._set(dn)

    def test_does_not_fail_if_wrong_args(self):
        gui_core_context = _GuiCoreContext(Mock(Gui))
        gui_core_context.update_data(state=Mock(), id="", payload={})
        gui_core_context.update_data(state=Mock(), id="", payload={"args": "wrong_args"})
        gui_core_context.update_data(state=Mock(), id="", payload={"args": ["wrong_args"]})

    def test_do_not_update_data_if_not_readable(self):
        with patch("taipy.gui_core._context.is_readable", side_effect=is_false):
            with patch("taipy.gui_core._context.core_get", side_effect=core_get) as mock_core_get:
                with patch.object(DataNode, "write") as mock_write:
                    mockGui = Mock(Gui)
                    mockGui._get_client_id = lambda: "a_client_id"
                    gui_core_context = _GuiCoreContext(mockGui)
                    assign = Mock()
                    gui_core_context.update_data(
                        state=MockState(assign=assign),
                        id="",
                        payload={"args": [{"id": dn.id,"error_id": "error_var"}]},
                    )
                    mock_core_get.assert_not_called()
                    mock_write.assert_not_called()
                    assign.assert_called_once_with("error_var", f"Data node {dn.id} is not readable: foo.")

    def test_do_not_update_data_if_not_editable(self):
        with patch("taipy.gui_core._context.is_readable", side_effect=is_true):
            with patch("taipy.gui_core._context.is_editable", side_effect=is_false):
                with patch("taipy.gui_core._context.core_get", side_effect=core_get) as mock_core_get:
                    with patch.object(DataNode, "write") as mock_write:
                        mockGui = Mock(Gui)
                        mockGui._get_client_id = lambda: "a_client_id"
                        gui_core_context = _GuiCoreContext(mockGui)
                        assign = Mock()
                        gui_core_context.update_data(
                            state=MockState(assign=assign),
                            id="",
                            payload={"args": [{"id": dn.id,"error_id": "error_var"}]},
                        )
                        mock_core_get.assert_not_called()
                        mock_write.assert_not_called()
                        assign.assert_called_once_with("error_var", f"Data node {dn.id} is not editable: foo.")

    def test_write_str_data_with_editor_and_comment(self):
        with patch("taipy.gui_core._context.is_readable", side_effect=is_true):
            with patch("taipy.gui_core._context.is_editable", side_effect=is_true):
                with patch("taipy.gui_core._context.core_get", side_effect=core_get) as mock_core_get:
                    with patch.object(DataNode, "write") as mock_write:
                        mockGui = Mock(Gui)
                        mockGui._get_client_id = lambda: "a_client_id"
                        gui_core_context = _GuiCoreContext(mockGui)
                        assign = Mock()
                        gui_core_context.update_data(
                            state=MockState(assign=assign),
                            id="",
                            payload={
                                "args": [{
                                    "id": dn.id,
                                    "value": "data to write",
                                    "comment": "The comment",
                                    "error_id": "error_var"}],
                            },
                        )
                        mock_core_get.assert_called_once_with(dn.id)
                        mock_write.assert_called_once_with("data to write",
                                                           editor_id="a_client_id",
                                                           comment="The comment")
                        assign.assert_called_once_with("error_var", "")

    def test_write_date_data_with_editor_and_comment(self):
        with patch("taipy.gui_core._context.is_readable", side_effect=is_true):
            with patch("taipy.gui_core._context.is_editable", side_effect=is_true):
                with patch("taipy.gui_core._context.core_get", side_effect=core_get) as mock_core_get:
                    with patch.object(DataNode, "write") as mock_write:
                        mockGui = Mock(Gui)
                        mockGui._get_client_id = lambda: "a_client_id"
                        gui_core_context = _GuiCoreContext(mockGui)
                        assign = Mock()
                        date = datetime(2000, 1, 1, 0, 0, 0)
                        gui_core_context.update_data(
                            state=MockState(assign=assign),
                            id="",
                            payload={
                                "args": [
                                    {
                                        "id": dn.id,
                                        "value": "2000-01-01 00:00:00",
                                        "type": "date",
                                        "comment": "The comment",
                                        "error_id": "error_var"
                                    }],
                            },
                        )
                        mock_core_get.assert_called_once_with(dn.id)
                        mock_write.assert_called_once_with(date,
                                                           editor_id="a_client_id",
                                                           comment="The comment")
                        assign.assert_called_once_with("error_var", "")

    def test_write_int_data_with_editor_and_comment(self):
        with patch("taipy.gui_core._context.is_readable", side_effect=is_true):
            with patch("taipy.gui_core._context.is_editable", side_effect=is_true):
                with patch("taipy.gui_core._context.core_get", side_effect=core_get) as mock_core_get:
                    with patch.object(DataNode, "write") as mock_write:
                        mockGui = Mock(Gui)
                        mockGui._get_client_id = lambda: "a_client_id"
                        gui_core_context = _GuiCoreContext(mockGui)
                        assign = Mock()
                        gui_core_context.update_data(
                            state=MockState(assign=assign),
                            id="",
                            payload={
                                "args": [{"id": dn.id, "value": "1", "type": "int", "error_id": "error_var"}],
                            },
                        )
                        mock_core_get.assert_called_once_with(dn.id)
                        mock_write.assert_called_once_with(1, editor_id="a_client_id", comment=None)
                        assign.assert_called_once_with("error_var", "")

    def test_write_float_data_with_editor_and_comment(self):
        with patch("taipy.gui_core._context.is_readable", side_effect=is_true):
            with patch("taipy.gui_core._context.is_editable", side_effect=is_true):
                with patch("taipy.gui_core._context.core_get", side_effect=core_get) as mock_core_get:
                    with patch.object(DataNode, "write") as mock_write:
                        mockGui = Mock(Gui)
                        mockGui._get_client_id = lambda: "a_client_id"
                        gui_core_context = _GuiCoreContext(mockGui)
                        assign = Mock()
                        gui_core_context.update_data(
                            state=MockState(assign=assign),
                            id="",
                            payload={
                                "args": [{"id": dn.id, "value": "1.9", "type": "float", "error_id": "error_var"}],
                            },
                        )
                        mock_core_get.assert_called_once_with(dn.id)
                        mock_write.assert_called_once_with(1.9, editor_id="a_client_id", comment=None)
                        assign.assert_called_once_with("error_var", "")

    def test_fails_and_catch_the_error(self):
        with patch("taipy.gui_core._context.is_readable", side_effect=is_true):
            with patch("taipy.gui_core._context.is_editable", side_effect=is_true):
                with patch("taipy.gui_core._context.core_get", side_effect=core_get) as mock_core_get:
                    with patch.object(DataNode, "write", side_effect=fails) as mock_write:
                        mockGui = Mock(Gui)
                        mockGui._get_client_id = lambda: "a_client_id"
                        gui_core_context = _GuiCoreContext(mockGui)
                        assign = Mock()
                        gui_core_context.update_data(
                            state=MockState(assign=assign),
                            id="",
                            payload={
                                "args": [{"id": dn.id, "value": "1.9", "type": "float", "error_id": "error_var"}],
                            },
                        )
                        mock_core_get.assert_called_once_with(dn.id)
                        mock_write.assert_called_once_with(1.9, editor_id="a_client_id", comment=None)
                        assign.assert_called_once()
                        assert assign.call_args_list[0].args[0] == "error_var"
                        assert "Error updating Data node value." in assign.call_args_list[0].args[1]
