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
import traceback

from taipy import Job, JobId, Scope, Status, Task
from taipy.core._orchestrator._dispatcher import _JobDispatcher
from taipy.core._orchestrator._orchestrator_factory import _OrchestratorFactory
from taipy.core.data import InMemoryDataNode
from taipy.core.data._data_manager_factory import _DataManagerFactory
from taipy.core.data.data_node_id import EDIT_JOB_ID_KEY, EDIT_TIMESTAMP_KEY
from taipy.core.job._job_manager_factory import _JobManagerFactory
from taipy.core.task._task_manager_factory import _TaskManagerFactory


def nothing(*args):
    return 42


def _error():
    raise RuntimeError("Something bad has happened")


def test_update_job_status_no_exception():
    output = InMemoryDataNode("data_node", scope=Scope.SCENARIO)
    _DataManagerFactory._build_manager()._repository._save(output)
    task = Task("config_id", {}, nothing, output=[output])
    _TaskManagerFactory._build_manager()._repository._save(task)
    job = Job(JobId("id"), task, "s_id", task.id)
    _JobManagerFactory._build_manager()._repository._save(job)

    _JobDispatcher(_OrchestratorFactory._orchestrator)._update_job_status(job, None)

    assert job.status == Status.COMPLETED
    assert job.stacktrace == []
    assert len(output.edits) == 1
    assert len(output.edits[0]) == 2
    assert output.edits[0][EDIT_JOB_ID_KEY] == job.id
    assert output.edits[0][EDIT_TIMESTAMP_KEY] is not None
    assert output.last_edit_date is not None
    assert output.editor_id is None
    assert output.editor_expiration_date is None
    assert not output.edit_in_progress


def test_update_job_status_with_one_exception():
    task = Task("config_id", {}, nothing)
    _TaskManagerFactory._build_manager()._repository._save(task)
    job = Job(JobId("id"), task, "s_id", task.id)
    _JobManagerFactory._build_manager()._repository._save(job)
    e = Exception("test")
    _JobDispatcher(_OrchestratorFactory._orchestrator)._update_job_status(job, [e])

    assert job.status == Status.FAILED
    assert len(job.stacktrace) == 1
    assert job.stacktrace[0] == "".join(traceback.format_exception(type(e), value=e, tb=e.__traceback__))


def test_update_job_status_with_exceptions():
    task = Task("config_id", {}, nothing)
    _TaskManagerFactory._build_manager()._repository._save(task)
    job = Job(JobId("id"), task, "s_id", task.id)
    _JobManagerFactory._build_manager()._repository._save(job)
    e_1 = Exception("test1")
    e_2 = Exception("test2")
    _JobDispatcher(_OrchestratorFactory._orchestrator)._update_job_status(job, [e_1, e_2])

    assert job.status == Status.FAILED
    assert len(job.stacktrace) == 2
    assert job.stacktrace[0] == "".join(traceback.format_exception(type(e_1), value=e_1, tb=e_1.__traceback__))
    assert job.stacktrace[1] == "".join(traceback.format_exception(type(e_2), value=e_2, tb=e_2.__traceback__))
