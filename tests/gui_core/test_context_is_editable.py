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

from unittest.mock import Mock, patch

from taipy.config.common.scope import Scope
from taipy.core import Job, JobId, Scenario, Task
from taipy.core.data.pickle import PickleDataNode
from taipy.gui import Gui
from taipy.gui_core._context import _GuiCoreContext

a_scenario = Scenario("scenario_config_id", None, {}, sequences={"sequence": {}})
a_task = Task("task_config_id", {}, print)
a_job = Job(JobId("JOB_job_id"), a_task, "submit_id", a_scenario.id)
a_job.isfinished = lambda s: True  # type: ignore[attr-defined]
a_datanode = PickleDataNode("data_node_config_id", Scope.SCENARIO)


def mock_core_get(entity_id):
    if entity_id == a_scenario.id:
        return a_scenario
    if entity_id == a_job.id:
        return a_job
    if entity_id == a_datanode.id:
        return a_datanode
    return a_task


def mock_is_editable_false(entity_id):
    return False


def mock_is_true(entity_id):
    return True


class MockState:
    def __init__(self, **kwargs) -> None:
        self.assign = kwargs.get("assign")


class TestGuiCoreContext_is_editable:
    def test_crud_scenario(self):
        with patch("taipy.gui_core._context.core_get", side_effect=mock_core_get):
            gui_core_context = _GuiCoreContext(Mock())
            assign = Mock()
            gui_core_context.crud_scenario(
                MockState(assign=assign),
                "",
                {
                    "args": [
                        "",
                        "",
                        "",
                        True,
                        False,
                        {"name": "name", "id": a_scenario.id},
                    ],
                    "error_id": "error_var",
                },
            )
            assign.assert_not_called()

            with patch("taipy.gui_core._context.is_editable", side_effect=mock_is_editable_false):
                assign.reset_mock()
                gui_core_context.crud_scenario(
                    MockState(assign=assign),
                    "",
                    {
                        "args": [
                            "",
                            "",
                            "",
                            True,
                            False,
                            {"name": "name", "id": a_scenario.id},
                        ],
                        "error_id": "error_var",
                    },
                )
                assign.assert_called_once()
                assert assign.call_args.args[0] == "error_var"
                assert "is not editable" in str(assign.call_args.args[1])

    def test_edit_entity(self):
        with patch("taipy.gui_core._context.core_get", side_effect=mock_core_get):
            gui_core_context = _GuiCoreContext(Mock())
            assign = Mock()
            gui_core_context.edit_entity(
                MockState(assign=assign),
                "",
                {
                    "args": [
                        {"name": "name", "id": a_scenario.id},
                    ],
                    "error_id": "error_var",
                },
            )
            assign.assert_called_once()
            assert assign.call_args.args[0] == "error_var"
            assert assign.call_args.args[1] == ""

            with patch("taipy.gui_core._context.is_editable", side_effect=mock_is_editable_false):
                assign.reset_mock()
                gui_core_context.edit_entity(
                    MockState(assign=assign),
                    "",
                    {
                        "args": [
                            {"name": "name", "id": a_scenario.id},
                        ],
                        "error_id": "error_var",
                    },
                )
                assign.assert_called_once()
                assert assign.call_args.args[0] == "error_var"
                assert "is not editable" in str(assign.call_args.args[1])

    def test_act_on_jobs(self):
        with patch("taipy.gui_core._context.core_get", side_effect=mock_core_get), patch(
            "taipy.gui_core._context.is_deletable", side_effect=mock_is_true
        ):
            gui_core_context = _GuiCoreContext(Mock())
            assign = Mock()
            gui_core_context.act_on_jobs(
                MockState(assign=assign),
                "",
                {
                    "args": [
                        {"id": [a_job.id], "action": "cancel"},
                    ],
                    "error_id": "error_var",
                },
            )
            assign.assert_called_once()
            assert assign.call_args.args[0] == "error_var"
            assert "is not editable" not in assign.call_args.args[1]
            assign.reset_mock()

            with patch("taipy.gui_core._context.is_readable", side_effect=mock_is_editable_false):
                gui_core_context.act_on_jobs(
                    MockState(assign=assign),
                    "",
                    {
                        "args": [
                            {"id": [a_job.id], "action": "cancel"},
                        ],
                        "error_id": "error_var",
                    },
                )
                assign.assert_called_once()
                assert assign.call_args.args[0] == "error_var"
                assert "is not readable" in assign.call_args.args[1]

    def test_edit_data_node(self):
        with patch("taipy.gui_core._context.core_get", side_effect=mock_core_get):
            gui_core_context = _GuiCoreContext(Mock())
            assign = Mock()
            gui_core_context.edit_data_node(
                MockState(assign=assign),
                "",
                {
                    "args": [
                        {"id": a_datanode.id},
                    ],
                    "error_id": "error_var",
                },
            )
            assign.assert_called_once()
            assert assign.call_args.args[0] == "error_var"
            assert assign.call_args.args[1] == ""

            with patch("taipy.gui_core._context.is_editable", side_effect=mock_is_editable_false):
                assign.reset_mock()
                gui_core_context.edit_data_node(
                    MockState(assign=assign),
                    "",
                    {
                        "args": [
                            {"id": a_datanode.id},
                        ],
                        "error_id": "error_var",
                    },
                )
                assign.assert_called_once()
                assert assign.call_args.args[0] == "error_var"
                assert "is not editable" in assign.call_args.args[1]

    def test_lock_datanode_for_edit(self):
        with patch("taipy.gui_core._context.core_get", side_effect=mock_core_get):
            mockGui = Mock(Gui)
            mockGui._get_client_id = lambda: "a_client_id"
            gui_core_context = _GuiCoreContext(mockGui)
            assign = Mock()
            gui_core_context.lock_datanode_for_edit(
                MockState(assign=assign),
                "",
                {
                    "args": [
                        {"id": a_datanode.id},
                    ],
                    "error_id": "error_var",
                },
            )
            assign.assert_called_once()
            assert assign.call_args.args[0] == "error_var"
            assert assign.call_args.args[1] == ""

            with patch("taipy.gui_core._context.is_editable", side_effect=mock_is_editable_false):
                assign.reset_mock()
                gui_core_context.lock_datanode_for_edit(
                    MockState(assign=assign),
                    "",
                    {
                        "args": [
                            {"id": a_datanode.id},
                        ],
                        "error_id": "error_var",
                    },
                )
                assign.assert_called_once()
                assert assign.call_args.args[0] == "error_var"
                assert "is not editable" in assign.call_args.args[1]

    def test_update_data(self):
        with patch("taipy.gui_core._context.core_get", side_effect=mock_core_get):
            mockGui = Mock(Gui)
            mockGui._get_client_id = lambda: "a_client_id"
            gui_core_context = _GuiCoreContext(mockGui)
            assign = Mock()
            gui_core_context.update_data(
                MockState(assign=assign),
                "",
                {
                    "args": [
                        {"id": a_datanode.id},
                    ],
                    "error_id": "error_var",
                },
            )
            assign.assert_called()
            assert assign.call_args_list[0].args[0] == "error_var"
            assert assign.call_args_list[0].args[1] == ""
            assign.reset_mock()

            with patch("taipy.gui_core._context.is_editable", side_effect=mock_is_editable_false):
                gui_core_context.update_data(
                    MockState(assign=assign),
                    "",
                    {
                        "args": [
                            {"id": a_datanode.id},
                        ],
                        "error_id": "error_var",
                    },
                )
                assign.assert_called_once()
                assert assign.call_args.args[0] == "error_var"
                assert "is not editable" in assign.call_args.args[1]

    def test_tabular_data_edit(self):
        with patch("taipy.gui_core._context.core_get", side_effect=mock_core_get):
            mockGui = Mock(Gui)
            mockGui._get_client_id = lambda: "a_client_id"
            gui_core_context = _GuiCoreContext(mockGui)
            assign = Mock()
            gui_core_context.tabular_data_edit(
                MockState(assign=assign),
                "",
                {
                    "user_data": {"dn_id": a_datanode.id},
                    "error_id": "error_var",
                },
            )
            assign.assert_called_once()
            assert assign.call_args_list[0].args[0] == "error_var"
            assert "tabular value: type does not support at[] indexer" in assign.call_args_list[0].args[1]
            assign.reset_mock()

            with patch("taipy.gui_core._context.is_editable", side_effect=mock_is_editable_false):
                gui_core_context.tabular_data_edit(
                    MockState(assign=assign),
                    "",
                    {
                        "user_data": {"dn_id": a_datanode.id},
                        "error_id": "error_var",
                    },
                )
                assign.assert_called_once()
                assert assign.call_args.args[0] == "error_var"
                assert "is not editable" in assign.call_args.args[1]
