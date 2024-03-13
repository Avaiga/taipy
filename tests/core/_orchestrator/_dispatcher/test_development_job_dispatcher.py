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

import traceback
from unittest.mock import patch

from taipy.core import JobId
from taipy.core._orchestrator._dispatcher import _DevelopmentJobDispatcher
from taipy.core._orchestrator._orchestrator_factory import _OrchestratorFactory
from taipy.core.job.job import Job
from taipy.core.task._task_manager_factory import _TaskManagerFactory
from taipy.core.task.task import Task


def nothing(*args):
    return


def create_task():
    task = Task("config_id", {}, nothing, [], [])
    _TaskManagerFactory._build_manager()._set(task)
    return task


def test_dispatch_executes_the_function_no_exception():
    task = create_task()
    job = Job(JobId("job"), task, "s_id", task.id)
    dispatcher = _OrchestratorFactory._build_dispatcher()

    with patch("taipy.core._orchestrator._dispatcher._task_function_wrapper._TaskFunctionWrapper.execute") as mck:
        mck.return_value = []
        dispatcher._dispatch(job)

        mck.assert_called_once()

    assert job.is_completed()
    assert job.stacktrace == []


def test_dispatch_executes_the_function_with_exceptions():
    task = create_task()
    job = Job(JobId("job"), task, "s_id", task.id)
    dispatcher = _OrchestratorFactory._build_dispatcher()
    e_1 = Exception("test")
    e_2 = Exception("test")

    with patch("taipy.core._orchestrator._dispatcher._task_function_wrapper._TaskFunctionWrapper.execute") as mck:
        mck.return_value = [e_1, e_2]
        dispatcher._dispatch(job)

        mck.assert_called_once()

    assert len(job.stacktrace) == 2
    assert job.stacktrace[1] == "".join(traceback.format_exception(type(e_2), value=e_2, tb=e_2.__traceback__))
    assert job.stacktrace[0] == "".join(traceback.format_exception(type(e_1), value=e_1, tb=e_1.__traceback__))
    assert job.is_failed()


def test_can_execute():
    dispatcher = _DevelopmentJobDispatcher(_OrchestratorFactory._orchestrator)
    assert dispatcher._can_execute()
