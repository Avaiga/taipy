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

import pytest

from taipy.common.config.common.scope import Scope
from taipy.core import Job, JobId, Scenario, Task
from taipy.core.data._data_manager_factory import _DataManagerFactory
from taipy.core.data.pickle import PickleDataNode
from taipy.core.job._job_manager_factory import _JobManagerFactory
from taipy.core.scenario._scenario_manager_factory import _ScenarioManagerFactory
from taipy.core.task._task_manager_factory import _TaskManagerFactory
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


def mock_is_promotable_false(entity_id):
    return False


def mock_is_true(entity_id):
    return True


class MockState:
    def __init__(self, **kwargs) -> None:
        self.assign = kwargs.get("assign")


class TestGuiCoreContext_is_promotable:
    @pytest.fixture(scope="class", autouse=True)
    def set_entity(self):
        _ScenarioManagerFactory._build_manager()._set(a_scenario)
        _TaskManagerFactory._build_manager()._set(a_task)
        _JobManagerFactory._build_manager()._set(a_job)
        _DataManagerFactory._build_manager()._set(a_datanode)

    def test_edit_entity(self):
        with (
            patch("taipy.gui_core._context.core_get", side_effect=mock_core_get),
            patch("taipy.gui_core._context.is_promotable", side_effect=mock_is_true),
        ):
            gui_core_context = _GuiCoreContext(Mock())
            assign = Mock()
            gui_core_context.edit_entity(
                MockState(assign=assign),
                "",
                {
                    "args": [
                        {"name": "name", "id": a_scenario.id, "primary": True},
                    ],
                    "error_id": "error_var",
                },
            )
            assign.assert_called_once()
            assert assign.call_args.args[0] == "error_var"
            assert "to primary because it doesn't belong to a cycle" in assign.call_args.args[1]
            assign.reset_mock()

            with patch("taipy.gui_core._context.is_promotable", side_effect=mock_is_promotable_false):
                gui_core_context.edit_entity(
                    MockState(assign=assign),
                    "",
                    {
                        "args": [
                            {"name": "name", "id": a_scenario.id, "primary": True},
                        ],
                        "error_id": "error_var",
                    },
                )
                assign.assert_called_once()
                assert assign.call_args.args[0] == "error_var"
                assert "is not promotable" in assign.call_args.args[1]
