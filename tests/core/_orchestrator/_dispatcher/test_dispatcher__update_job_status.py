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

from taipy import Job, JobId, Status, Task
from taipy.core._orchestrator._dispatcher import _JobDispatcher
from taipy.core._orchestrator._orchestrator_factory import _OrchestratorFactory
from taipy.core.job._job_manager_factory import _JobManagerFactory
from taipy.core.task._task_manager_factory import _TaskManagerFactory


def nothing(*args):
    pass


def test_update_job_status_no_exception():
    task = Task("config_id", {}, nothing)
    _TaskManagerFactory._build_manager()._set(task)
    job = Job(JobId("id"), task, "s_id", task.id)
    _JobManagerFactory._build_manager()._set(job)

    _JobDispatcher(_OrchestratorFactory._orchestrator)._update_job_status(job, None)

    assert job.status == Status.COMPLETED
    assert job.stacktrace == []


def test_update_job_status_with_one_exception():
    task = Task("config_id", {}, nothing)
    _TaskManagerFactory._build_manager()._set(task)
    job = Job(JobId("id"), task, "s_id", task.id)
    _JobManagerFactory._build_manager()._set(job)
    e = Exception("test")
    _JobDispatcher(_OrchestratorFactory._orchestrator)._update_job_status(job, [e])

    assert job.status == Status.FAILED
    assert len(job.stacktrace) == 1
    assert job.stacktrace[0] == "".join(traceback.format_exception(type(e), value=e, tb=e.__traceback__))


def test_update_job_status_with_exceptions():
    task = Task("config_id", {}, nothing)
    _TaskManagerFactory._build_manager()._set(task)
    job = Job(JobId("id"), task, "s_id", task.id)
    _JobManagerFactory._build_manager()._set(job)
    e_1 = Exception("test1")
    e_2 = Exception("test2")
    _JobDispatcher(_OrchestratorFactory._orchestrator)._update_job_status(job, [e_1, e_2])

    assert job.status == Status.FAILED
    assert len(job.stacktrace) == 2
    assert job.stacktrace[0] == "".join(traceback.format_exception(type(e_1), value=e_1, tb=e_1.__traceback__))
    assert job.stacktrace[1] == "".join(traceback.format_exception(type(e_2), value=e_2, tb=e_2.__traceback__))
