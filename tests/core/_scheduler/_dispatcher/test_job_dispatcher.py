# Copyright 2022 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import glob
import multiprocessing
import os
from datetime import datetime
from functools import partial
from time import sleep
from unittest import mock
from unittest.mock import MagicMock

import pytest

from taipy.core._scheduler._dispatcher._standalone_job_dispatcher import _StandaloneJobDispatcher
from taipy.core._scheduler._scheduler import _Scheduler
from taipy.core.common.alias import DataNodeId, JobId, TaskId
from taipy.core.config import JobConfig
from taipy.core.config.config import Config
from taipy.core.data._data_manager import _DataManager
from taipy.core.job.job import Job
from taipy.core.task.task import Task


@pytest.fixture(scope="function", autouse=True)
def reset_configuration_singleton():
    yield

    for f in glob.glob("*.p"):
        print(f"deleting file {f}")
        os.remove(f)


def execute(lock):
    with lock:
        ...
    return None


def _error():
    raise RuntimeError("Something bad has happened")


def test_can_execute_2_workers():
    Config.configure_job_executions(nb_of_workers=2)
    m = multiprocessing.Manager()
    lock = m.Lock()

    task_id = TaskId("task_id1")
    task = Task(
        config_id="name",
        input=[],
        function=partial(execute, lock),
        output=[_DataManager._get_or_create(Config.configure_data_node("input1", default_data=21))],
        id=task_id,
    )
    job_id = JobId("id1")
    job = Job(job_id, task)

    dispatcher = _StandaloneJobDispatcher()

    with lock:
        assert dispatcher._can_execute()
        dispatcher._dispatch(job)
        assert dispatcher._can_execute()
        dispatcher._dispatch(job)
        assert not dispatcher._can_execute()

    assert_true_after_120_second_max(lambda: dispatcher._can_execute())


def test_can_execute_synchronous():
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)
    _Scheduler._update_job_config()

    task_id = TaskId("task_id1")
    task = Task(config_id="name", input=[], function=print, output=[], id=task_id)
    job_id = JobId("id1")
    job = Job(job_id, task)

    dispatcher = _Scheduler._dispatcher

    assert dispatcher._can_execute()
    dispatcher._dispatch(job)
    assert dispatcher._can_execute()


def test_exception_in_user_function():
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)
    _Scheduler._update_job_config()

    task_id = TaskId("task_id1")
    job_id = JobId("id1")
    task = Task(config_id="name", input=[], function=_error, output=[], id=task_id)
    job = Job(job_id, task)

    dispatcher = _Scheduler._dispatcher
    dispatcher._dispatch(job)
    assert job.is_failed()
    assert 'RuntimeError("Something bad has happened")' in str(job.stacktrace[0])


def test_exception_in_writing_data():
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)
    _Scheduler._update_job_config()

    task_id = TaskId("task_id1")
    job_id = JobId("id1")
    output = MagicMock()
    output.id = DataNodeId("output_id")
    output.config_id = "my_raising_datanode"
    output._is_in_cache = False
    output.write.side_effect = ValueError()
    task = Task(config_id="name", input=[], function=print, output=[output], id=task_id)
    job = Job(job_id, task)

    dispatcher = _Scheduler._dispatcher

    with mock.patch("taipy.core.data._data_manager._DataManager._get") as get:
        get.return_value = output
        dispatcher._dispatch(job)
        assert job.is_failed()
        assert "node" in job.stacktrace[0]


def assert_true_after_120_second_max(assertion):
    start = datetime.now()
    while (datetime.now() - start).seconds < 120:
        sleep(0.1)  # Limit CPU usage
        if assertion():
            return
    assert assertion()
