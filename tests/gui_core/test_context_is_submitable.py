from unittest.mock import Mock, patch

import pytest

from src.taipy.gui_core._context import _GuiCoreContext
from taipy.config.common.scope import Scope
from taipy.core import Job, Scenario, Task
from taipy.core.data.pickle import PickleDataNode

a_scenario = Scenario("scenario_config_id", [], {}, sequences={"sequence": {}})
a_task = Task("task_config_id", {}, print)
a_job = Job("JOB_job_id", a_task, "submit_id", a_scenario.id)
a_job.isfinished = lambda s: True
a_datanode = PickleDataNode("data_node_config_id", Scope.SCENARIO)


def mock_is_submittable_false(entity_id):
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
    return a_task


class MockState:
    def __init__(self, **kwargs) -> None:
        self.assign = kwargs.get("assign")


class TestGuiCoreContext_is_submittable:
    def test_submit_entity(self):
        with patch("src.taipy.gui_core._context.core_get", side_effect=mock_core_get), patch(
            "src.taipy.gui_core._context.is_submittable", side_effect=mock_is_true
        ):
            gui_core_context = _GuiCoreContext(Mock())
            assign = Mock()
            gui_core_context.submit_entity(
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
            assert str(assign.call_args.args[1]).startswith("Error submitting entity.")

            with patch("src.taipy.gui_core._context.is_submittable", side_effect=mock_is_submittable_false):
                assign.reset_mock()
                gui_core_context.submit_entity(
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
                assert str(assign.call_args.args[1]).endswith("is not submittable.")
