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
from taipy.core.reason.reason import Reason
from taipy.gui_core._context import _GuiCoreContext

a_scenario = Scenario("scenario_config_id", None, {}, sequences={"sequence": {}})
a_task = Task("task_config_id", {}, print)
a_job = Job(JobId("JOB_job_id"), a_task, "submit_id", a_scenario.id)
a_job.isfinished = lambda s: True  # type: ignore[attr-defined]
a_datanode = PickleDataNode("data_node_config_id", Scope.SCENARIO)


def mock_is_submittable_reason(entity_id):
    reason = Reason(entity_id)
    reason._add_reason(entity_id, "a reason")
    return reason


def mock_has_no_reason(entity_id):
    return Reason(entity_id)


def mock_core_get(entity_id):
    if entity_id == a_scenario.id:
        return a_scenario
    if entity_id == a_job.id:
        return a_job
    if entity_id == a_datanode.id:
        return a_datanode
    return a_task


class MockState:
    def __init__(self, **kwargs) -> None:
        self.assign = kwargs.get("assign")


class TestGuiCoreContext_is_submittable:
    def test_submit_entity(self):
        with patch("taipy.gui_core._context.core_get", side_effect=mock_core_get), patch(
            "taipy.gui_core._context.is_submittable", side_effect=mock_has_no_reason
        ):
            gui_core_context = _GuiCoreContext(Mock())
            assign = Mock()
            gui_core_context.submit_entity(
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
            assert str(assign.call_args.args[1]).startswith("Error submitting entity.")

            with patch("taipy.gui_core._context.is_submittable", side_effect=mock_is_submittable_reason):
                assign.reset_mock()
                gui_core_context.submit_entity(
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
                assert "is not submittable" in str(assign.call_args.args[1])
