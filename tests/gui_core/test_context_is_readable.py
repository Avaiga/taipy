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

import typing as t
from unittest.mock import Mock, patch

from taipy.config.common.scope import Scope
from taipy.core import Job, JobId, Scenario, Task
from taipy.core.data.pickle import PickleDataNode
from taipy.core.submission.submission import Submission
from taipy.gui import Gui
from taipy.gui_core._context import _GuiCoreContext

a_scenario = Scenario("scenario_config_id", None, {}, sequences={"sequence": {}})
a_task = Task("task_config_id", {}, print)
a_job = Job(t.cast(JobId, "JOB_job_id"), a_task, "submit_id", a_scenario.id)
a_job.isfinished = lambda s: True  # type: ignore[attr-defined]
a_datanode = PickleDataNode("data_node_config_id", Scope.SCENARIO)
a_submission = Submission(a_scenario.id, "Scenario", a_scenario.config_id)


def mock_is_readable_false(entity_id):
    return False


def mock_is_true(entity_id):
    return True


def mock_core_get(entity_id):
    if entity_id == a_scenario.id:
        return a_scenario
    if entity_id == a_job.id:
        return a_job
    if entity_id == a_datanode.id:
        return a_datanode
    if entity_id == a_submission.id:
        return a_submission
    return a_task


class MockState:
    def __init__(self, **kwargs) -> None:
        self.assign = kwargs.get("assign")


class TestGuiCoreContext_is_readable:
    def test_scenario_adapter(self):
        with patch("taipy.gui_core._context.core_get", side_effect=mock_core_get):
            gui_core_context = _GuiCoreContext(Mock())
            outcome = gui_core_context.scenario_adapter(a_scenario)
            assert isinstance(outcome, tuple)
            assert outcome[0] == a_scenario.id

            with patch("taipy.gui_core._context.is_readable", side_effect=mock_is_readable_false):
                outcome = gui_core_context.scenario_adapter(a_scenario)
                assert outcome is None

    def test_get_scenario_by_id(self):
        with patch("taipy.gui_core._context.core_get", side_effect=mock_core_get):
            gui_core_context = _GuiCoreContext(Mock())
            outcome = gui_core_context.get_scenario_by_id(a_scenario.id)
            assert outcome is not None

            with patch("taipy.gui_core._context.is_readable", side_effect=mock_is_readable_false):
                outcome = gui_core_context.get_scenario_by_id(a_scenario.id)
                assert outcome is None

    def test_crud_scenario(self):
        with patch("taipy.gui_core._context.core_get", side_effect=mock_core_get):
            gui_core_context = _GuiCoreContext(Mock())
            assign = Mock()
            gui_core_context.crud_scenario(
                MockState(assign=assign),
                "",
                {
                    "args": [
                        True,
                        False,
                        {"name": "name", "id": a_scenario.id},
                    ]
                },
            )
            assign.assert_not_called()

            with patch("taipy.gui_core._context.is_readable", side_effect=mock_is_readable_false):
                assign.reset_mock()
                gui_core_context.crud_scenario(
                    MockState(assign=assign),
                    "",
                    {
                        "args": [
                            True,
                            False,
                            {"name": "name", "id": a_scenario.id},
                        ]
                    },
                )
                assign.assert_called_once()
                assert assign.call_args.args[0] == "gui_core_sc_error"
                assert str(assign.call_args.args[1]).endswith("is not readable.")

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
                    ]
                },
            )
            assign.assert_called_once()
            assert assign.call_args.args[0] == "gui_core_sv_error"
            assert assign.call_args.args[1] == ""

            with patch("taipy.gui_core._context.is_readable", side_effect=mock_is_readable_false):
                assign.reset_mock()
                gui_core_context.edit_entity(
                    MockState(assign=assign),
                    "",
                    {
                        "args": [
                            {"name": "name", "id": a_scenario.id},
                        ]
                    },
                )
                assign.assert_called_once()
                assert assign.call_args.args[0] == "gui_core_sv_error"
                assert str(assign.call_args.args[1]).endswith("is not readable.")

    def test_scenario_status_callback(self):
        with patch("taipy.gui_core._context.core_get", side_effect=mock_core_get) as mockget:
            mockget.reset_mock()
            gui_core_context = _GuiCoreContext(Mock())

            def sub_cb():
                return True

            gui_core_context.client_submission[a_submission.id] = a_submission.submission_status
            gui_core_context.scenario_status_callback(a_submission.id)
            mockget.assert_called()
            found = False
            for call in mockget.call_args_list:
                if call.args[0] == a_scenario.id:
                    found = True
                    break
            assert found is True
            mockget.reset_mock()

            with patch("taipy.gui_core._context.is_readable", side_effect=mock_is_readable_false):
                gui_core_context.scenario_status_callback(a_submission.id)
                mockget.assert_not_called()

    def test_data_node_adapter(self):
        with patch("taipy.gui_core._context.core_get", side_effect=mock_core_get):
            gui_core_context = _GuiCoreContext(Mock())
            outcome = gui_core_context.data_node_adapter(a_datanode)
            assert isinstance(outcome, tuple)
            assert outcome[0] == a_datanode.id

            with patch("taipy.gui_core._context.is_readable", side_effect=mock_is_readable_false):
                outcome = gui_core_context.data_node_adapter(a_datanode)
                assert outcome is None

    def test_job_adapter(self):
        with patch("taipy.gui_core._context.core_get", side_effect=mock_core_get):
            gui_core_context = _GuiCoreContext(Mock())
            outcome = gui_core_context.job_adapter(a_job)
            assert isinstance(outcome, tuple)
            assert outcome[0] == a_job.id

            with patch("taipy.gui_core._context.is_readable", side_effect=mock_is_readable_false):
                outcome = gui_core_context.job_adapter(a_job)
                assert outcome is None

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
                        {"id": [a_job.id], "action": "delete"},
                    ]
                },
            )
            assign.assert_called_once()
            assert assign.call_args.args[0] == "gui_core_js_error"
            assert str(assign.call_args.args[1]).find("is not readable.") == -1
            assign.reset_mock()

            gui_core_context.act_on_jobs(
                MockState(assign=assign),
                "",
                {
                    "args": [
                        {"id": [a_job.id], "action": "cancel"},
                    ]
                },
            )
            assign.assert_called_once()
            assert assign.call_args.args[0] == "gui_core_js_error"
            assert str(assign.call_args.args[1]).find("is not readable.") == -1
            assign.reset_mock()

            with patch("taipy.gui_core._context.is_readable", side_effect=mock_is_readable_false):
                gui_core_context.act_on_jobs(
                    MockState(assign=assign),
                    "",
                    {
                        "args": [
                            {"id": [a_job.id], "action": "delete"},
                        ]
                    },
                )
                assign.assert_called_once()
                assert assign.call_args.args[0] == "gui_core_js_error"
                assert str(assign.call_args.args[1]).endswith("is not readable.")
                assign.reset_mock()

                gui_core_context.act_on_jobs(
                    MockState(assign=assign),
                    "",
                    {
                        "args": [
                            {"id": [a_job.id], "action": "cancel"},
                        ]
                    },
                )
                assign.assert_called_once()
                assert assign.call_args.args[0] == "gui_core_js_error"
                assert str(assign.call_args.args[1]).endswith("is not readable.")

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
                    ]
                },
            )
            assign.assert_called_once()
            assert assign.call_args.args[0] == "gui_core_dv_error"
            assert assign.call_args.args[1] == ""

            with patch("taipy.gui_core._context.is_readable", side_effect=mock_is_readable_false):
                assign.reset_mock()
                gui_core_context.edit_data_node(
                    MockState(assign=assign),
                    "",
                    {
                        "args": [
                            {"id": a_datanode.id},
                        ]
                    },
                )
                assign.assert_called_once()
                assert assign.call_args.args[0] == "gui_core_dv_error"
                assert str(assign.call_args.args[1]).endswith("is not readable.")

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
                    ]
                },
            )
            assign.assert_called_once()
            assert assign.call_args.args[0] == "gui_core_dv_error"
            assert assign.call_args.args[1] == ""

            with patch("taipy.gui_core._context.is_readable", side_effect=mock_is_readable_false):
                assign.reset_mock()
                gui_core_context.lock_datanode_for_edit(
                    MockState(assign=assign),
                    "",
                    {
                        "args": [
                            {"id": a_datanode.id},
                        ]
                    },
                )
                assign.assert_called_once()
                assert assign.call_args.args[0] == "gui_core_dv_error"
                assert str(assign.call_args.args[1]).endswith("is not readable.")

    def test_get_scenarios_for_owner(self):
        with patch("taipy.gui_core._context.core_get", side_effect=mock_core_get) as mockget:
            gui_core_context = _GuiCoreContext(Mock())
            gui_core_context.get_scenarios_for_owner(a_scenario.id)
            mockget.assert_called_once()
            mockget.reset_mock()

            with patch("taipy.gui_core._context.is_readable", side_effect=mock_is_readable_false):
                gui_core_context.scenario_status_callback(a_scenario.id)
                mockget.assert_not_called()

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
                    ]
                },
            )
            assign.assert_called()
            assert assign.call_args_list[0].args[0] == "gui_core_dv_error"
            assert assign.call_args_list[0].args[1] == ""
            assign.reset_mock()

            with patch("taipy.gui_core._context.is_readable", side_effect=mock_is_readable_false):
                gui_core_context.update_data(
                    MockState(assign=assign),
                    "",
                    {
                        "args": [
                            {"id": a_datanode.id},
                        ]
                    },
                )
                assign.assert_called_once()
                assert assign.call_args.args[0] == "gui_core_dv_error"
                assert str(assign.call_args.args[1]).endswith("is not readable.")

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
                },
            )
            assign.assert_called_once()
            assert assign.call_args_list[0].args[0] == "gui_core_dv_error"
            assert (
                assign.call_args_list[0].args[1]
                == "Error updating Datanode tabular value: type does not support at[] indexer."
            )
            assign.reset_mock()

            with patch("taipy.gui_core._context.is_readable", side_effect=mock_is_readable_false):
                gui_core_context.tabular_data_edit(
                    MockState(assign=assign),
                    "",
                    {
                        "user_data": {"dn_id": a_datanode.id},
                    },
                )
                assign.assert_called_once()
                assert assign.call_args.args[0] == "gui_core_dv_error"
                assert str(assign.call_args.args[1]).endswith("is not readable.")

    def test_get_data_node_tabular_data(self):
        with patch("taipy.gui_core._context.core_get", side_effect=mock_core_get) as mockget:
            gui_core_context = _GuiCoreContext(Mock())
            gui_core_context.get_data_node_tabular_data(a_datanode, a_datanode.id)
            mockget.assert_called_once()
            mockget.reset_mock()

            with patch("taipy.gui_core._context.is_readable", side_effect=mock_is_readable_false):
                gui_core_context.get_data_node_tabular_data(a_datanode, a_datanode.id)
                mockget.assert_not_called()

    def test_get_data_node_tabular_columns(self):
        with patch("taipy.gui_core._context.core_get", side_effect=mock_core_get) as mockget:
            gui_core_context = _GuiCoreContext(Mock())
            gui_core_context.get_data_node_tabular_columns(a_datanode, a_datanode.id)
            mockget.assert_called_once()
            mockget.reset_mock()

            with patch("taipy.gui_core._context.is_readable", side_effect=mock_is_readable_false):
                gui_core_context.get_data_node_tabular_columns(a_datanode, a_datanode.id)
                mockget.assert_not_called()

    def test_get_data_node_chart_config(self):
        with patch("taipy.gui_core._context.core_get", side_effect=mock_core_get) as mockget:
            gui_core_context = _GuiCoreContext(Mock())
            gui_core_context.get_data_node_chart_config(a_datanode, a_datanode.id)
            mockget.assert_called_once()
            mockget.reset_mock()

            with patch("taipy.gui_core._context.is_readable", side_effect=mock_is_readable_false):
                gui_core_context.get_data_node_chart_config(a_datanode, a_datanode.id)
                mockget.assert_not_called()
