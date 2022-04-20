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
import random
import string
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timedelta
from functools import partial
from queue import Queue
from time import sleep

import pytest

from taipy.core._scheduler._executor._synchronous import _Synchronous
from taipy.core._scheduler._scheduler import _Scheduler
from taipy.core.common.scope import Scope
from taipy.core.config._config import _Config
from taipy.core.config.config import Config
from taipy.core.data._data_manager import _DataManager
from taipy.core.data.in_memory import InMemoryDataNode
from taipy.core.job._job_manager import _JobManager
from taipy.core.job.job import Job, JobId
from taipy.core.job.status import Status
from taipy.core.task._task_manager import _TaskManager
from taipy.core.task.task import Task
from tests.core.utils import assert_true_after_1_minute_max


@pytest.fixture(scope="function", autouse=True)
def reset_configuration_singleton():
    yield
    Config._python_config = _Config()
    Config._file_config = None
    Config._env_file_config = None
    Config._applied_config = _Config._default_config()

    for f in glob.glob("*.p"):
        print(f"deleting file {f}")
        os.remove(f)


def multiply(nb1: float, nb2: float):
    sleep(0.1)
    return nb1 * nb2


def lock_multiply(lock, nb1: float, nb2: float):
    with lock:
        return multiply(nb1, nb2)


def test_submit_task():
    before_creation = datetime.now()
    sleep(0.1)
    task = _create_task(multiply)
    output_dn_id = task.output[f"{task.config_id}_output0"].id

    assert _DataManager._get(output_dn_id).last_edition_date > before_creation
    assert _DataManager._get(output_dn_id).job_ids == []
    assert _DataManager._get(output_dn_id).is_ready_for_reading

    before_submission_creation = datetime.now()
    sleep(0.1)
    job = _Scheduler.submit_task(task)
    sleep(0.1)
    after_submission_creation = datetime.now()
    assert _DataManager._get(output_dn_id).read() == 42
    assert _DataManager._get(output_dn_id).last_edition_date > before_submission_creation
    assert _DataManager._get(output_dn_id).last_edition_date < after_submission_creation
    assert _DataManager._get(output_dn_id).job_ids == [job.id]
    assert _DataManager._get(output_dn_id).is_ready_for_reading
    assert job.is_completed()


def test_submit_task_that_return_multiple_outputs():
    def return_2tuple(nb1, nb2):
        return multiply(nb1, nb2), multiply(nb1, nb2) / 2

    def return_list(nb1, nb2):
        return [multiply(nb1, nb2), multiply(nb1, nb2) / 2]

    with_tuple = _create_task(return_2tuple, 2)
    with_list = _create_task(return_list, 2)

    _Scheduler.submit_task(with_tuple)
    _Scheduler.submit_task(with_list)

    assert (
        with_tuple.output[f"{with_tuple.config_id}_output0"].read()
        == with_list.output[f"{with_list.config_id}_output0"].read()
        == 42
    )
    assert (
        with_tuple.output[f"{with_tuple.config_id}_output1"].read()
        == with_list.output[f"{with_list.config_id}_output1"].read()
        == 21
    )


def test_submit_task_returns_single_iterable_output():
    def return_2tuple(nb1, nb2):
        return multiply(nb1, nb2), multiply(nb1, nb2) / 2

    def return_list(nb1, nb2):
        return [multiply(nb1, nb2), multiply(nb1, nb2) / 2]

    task_with_tuple = _create_task(return_2tuple, 1)
    task_with_list = _create_task(return_list, 1)

    _Scheduler.submit_task(task_with_tuple)
    assert task_with_tuple.output[f"{task_with_tuple.config_id}_output0"].read() == (42, 21)
    _Scheduler.submit_task(task_with_list)
    assert task_with_list.output[f"{task_with_list.config_id}_output0"].read() == [42, 21]


def test_data_node_not_written_due_to_wrong_result_nb():
    def return_2tuple():
        return lambda nb1, nb2: (multiply(nb1, nb2), multiply(nb1, nb2) / 2)

    task = _create_task(return_2tuple(), 3)

    job = _Scheduler.submit_task(task)
    assert task.output[f"{task.config_id}_output0"].read() == 0
    assert job.is_failed()


def test_submit_task_in_parallel():
    m = multiprocessing.Manager()
    lock = m.Lock()

    _Scheduler._set_nb_of_workers(Config.configure_job_executions(nb_of_workers=2))
    task = _create_task(partial(lock_multiply, lock))

    with lock:
        job = _Scheduler.submit_task(task)
        assert task.output[f"{task.config_id}_output0"].read() == 0
        assert job.is_running()

    assert_true_after_1_minute_max(job.is_completed)


def test_submit_task_multithreading_multiple_task():
    _Scheduler._set_nb_of_workers(Config.configure_job_executions(nb_of_workers=2))

    m = multiprocessing.Manager()
    lock_1 = m.Lock()
    lock_2 = m.Lock()

    task_1 = _create_task(partial(lock_multiply, lock_1))
    task_2 = _create_task(partial(lock_multiply, lock_2))

    with lock_1:
        with lock_2:
            job_1 = _Scheduler.submit_task(task_1)
            job_2 = _Scheduler.submit_task(task_2)

            assert task_1.output[f"{task_1.config_id}_output0"].read() == 0
            assert task_2.output[f"{task_2.config_id}_output0"].read() == 0
            assert job_1.is_running()
            assert job_2.is_running()

        assert_true_after_1_minute_max(lambda: task_2.output[f"{task_2.config_id}_output0"].read() == 42)
        assert task_1.output[f"{task_1.config_id}_output0"].read() == 0
        assert_true_after_1_minute_max(job_2.is_completed)
        assert job_1.is_running()
        assert job_2.is_completed()

    assert_true_after_1_minute_max(lambda: task_1.output[f"{task_1.config_id}_output0"].read() == 42)
    assert task_2.output[f"{task_2.config_id}_output0"].read() == 42
    assert_true_after_1_minute_max(job_1.is_completed)
    assert job_2.is_completed()


def test_submit_task_multithreading_multiple_task_in_sync_way_to_check_job_status():
    _Scheduler._set_nb_of_workers(Config.configure_job_executions(nb_of_workers=2))

    m = multiprocessing.Manager()
    lock_0 = m.Lock()
    lock_1 = m.Lock()
    lock_2 = m.Lock()

    task_0 = _create_task(partial(lock_multiply, lock_0))
    task_1 = _create_task(partial(lock_multiply, lock_1))
    task_2 = _create_task(partial(lock_multiply, lock_2))

    with lock_0:
        _Scheduler.submit_task(task_0)
        with lock_1:
            with lock_2:
                job_1 = _Scheduler.submit_task(task_2)
                job_2 = _Scheduler.submit_task(task_1)

                assert task_1.output[f"{task_1.config_id}_output0"].read() == 0
                assert task_2.output[f"{task_2.config_id}_output0"].read() == 0
                assert job_1.is_running()
                assert job_2.is_pending()

            assert_true_after_1_minute_max(lambda: task_2.output[f"{task_2.config_id}_output0"].read() == 42)
            assert task_1.output[f"{task_1.config_id}_output0"].read() == 0
            assert_true_after_1_minute_max(job_1.is_completed)
            assert_true_after_1_minute_max(job_2.is_running)

    assert_true_after_1_minute_max(lambda: task_1.output[f"{task_1.config_id}_output0"].read() == 42)
    assert task_2.output[f"{task_2.config_id}_output0"].read() == 42
    assert job_1.is_completed()
    assert_true_after_1_minute_max(job_2.is_completed)


def test_blocked_task():
    _Scheduler._set_nb_of_workers(Config.configure_job_executions(nb_of_workers=2))

    m = multiprocessing.Manager()
    lock_1 = m.Lock()
    lock_2 = m.Lock()

    foo_cfg = Config.configure_data_node("foo", default_data=1)
    foo = _DataManager._get_or_create(foo_cfg)
    bar_cfg = Config.configure_data_node("bar")
    bar = _DataManager._get_or_create(bar_cfg)
    baz_cfg = Config.configure_data_node("baz")
    baz = _DataManager._get_or_create(baz_cfg)
    task_1 = Task("by_2", partial(lock_multiply, lock_1, 2), [foo], [bar])
    task_2 = Task("by_3", partial(lock_multiply, lock_2, 3), [bar], [baz])

    assert task_1.foo.is_ready_for_reading  # foo is ready
    assert not task_1.bar.is_ready_for_reading  # But bar is not ready
    assert not task_2.baz.is_ready_for_reading  # neither does baz

    assert len(_Scheduler.blocked_jobs) == 0
    job_2 = _Scheduler.submit_task(task_2)  # job 2 is submitted first
    assert job_2.is_blocked()  # since bar is not up_to_date the job 2 is blocked
    assert len(_Scheduler.blocked_jobs) == 1
    with lock_2:
        with lock_1:
            job_1 = _Scheduler.submit_task(task_1)  # job 1 is submitted and locked
            assert job_1.is_running()  # so it is still running
            assert not _DataManager._get(task_1.bar.id).is_ready_for_reading  # And bar still not ready
            assert job_2.is_blocked()  # the job_2 remains blocked
        assert_true_after_1_minute_max(job_1.is_completed)  # job1 unlocked and can complete
        assert _DataManager._get(task_1.bar.id).is_ready_for_reading  # bar becomes ready
        assert _DataManager._get(task_1.bar.id).read() == 2  # the data is computed and written
        assert_true_after_1_minute_max(job_2.is_running)  # And job 2 can start running
        assert len(_Scheduler.blocked_jobs) == 0
    assert_true_after_1_minute_max(job_2.is_completed)  # job 2 unlocked so it can complete
    assert _DataManager._get(task_2.baz.id).is_ready_for_reading  # baz becomes ready
    assert _DataManager._get(task_2.baz.id).read() == 6  # the data is computed and written


class MyScheduler(_Scheduler):
    @classmethod
    def getJobDispatcher(cls):
        return cls._dispatcher


def test_task_scheduler_create_synchronous_dispatcher():
    MyScheduler._set_nb_of_workers(Config.configure_job_executions())
    assert isinstance(MyScheduler.getJobDispatcher()._executor, _Synchronous)
    assert MyScheduler.getJobDispatcher()._nb_available_workers == 1


def test_task_scheduler_create_parallel_dispatcher():
    MyScheduler._set_nb_of_workers(Config.configure_job_executions(nb_of_workers=42))
    assert isinstance(MyScheduler.getJobDispatcher()._executor, ProcessPoolExecutor)
    assert MyScheduler.getJobDispatcher()._nb_available_workers == 42


def _create_task(function, nb_outputs=1):
    output_dn_config_id = "".join(random.choice(string.ascii_lowercase) for _ in range(10))
    input_dn = [
        _DataManager._get_or_create(Config.configure_data_node("input1", "pickle", Scope.PIPELINE, default_data=21)),
        _DataManager._get_or_create(Config.configure_data_node("input2", "pickle", Scope.PIPELINE, default_data=2)),
    ]
    output_dn = [
        _DataManager._get_or_create(
            Config.configure_data_node(f"{output_dn_config_id}_output{i}", "pickle", Scope.PIPELINE, default_data=0)
        )
        for i in range(nb_outputs)
    ]

    return Task(
        output_dn_config_id,
        function=function,
        input=input_dn,
        output=output_dn,
    )


def test_recover_jobs():
    _Scheduler._set_nb_of_workers(None)
    dn_inp = InMemoryDataNode('inp', Scope.PIPELINE, properties={'default_data': 'hello'})
    dn_inp_locked = InMemoryDataNode('inp_locked', Scope.PIPELINE, properties={'default_data': 'hello'})
    dn_inp_locked.lock_edition()

    task = Task('task', print, input=[dn_inp])
    task_locked = Task('task_locked', print, input=[dn_inp_locked])

    _DataManager._set(dn_inp)
    _DataManager._set(dn_inp_locked)
    _TaskManager._set(task)
    _TaskManager._set(task_locked)

    job_id_1 = JobId('job_1')
    job_1 = Job(job_id_1, task)
    job_1.creation_date = job_1.creation_date + timedelta(seconds=10)
    job_id_2 = JobId('job_2')
    job_2 = Job(job_id_2, task)
    job_2.creation_date = job_2.creation_date + timedelta(seconds=20)
    job_id_3 = JobId('job_3')
    job_3 = Job(job_id_3, task)
    job_3.creation_date = job_3.creation_date + timedelta(seconds=30)
    job_id_4 = JobId('job_4')
    job_4 = Job(job_id_4, task)
    job_4.creation_date = job_4.creation_date + timedelta(seconds=40)
    job_id_5 = JobId('job_5')
    job_5 = Job(job_id_5, task)
    job_5.creation_date = job_5.creation_date + timedelta(seconds=50)
    job_id_6 = JobId('job_6')
    job_6 = Job(job_id_6, task)
    job_6.creation_date = job_6.creation_date + timedelta(seconds=60)
    job_id_7 = JobId('job_7')
    job_7 = Job(job_id_7, task)
    job_7.creation_date = job_7.creation_date + timedelta(seconds=70)
    job_id_8 = JobId('job_8')
    job_8 = Job(job_id_8, task)
    job_8.creation_date = job_8.creation_date + timedelta(seconds=80)
    job_id_9 = JobId('job_9')
    job_9 = Job(job_id_9, task)
    job_9.creation_date = job_9.creation_date + timedelta(seconds=90)
    job_id_10 = JobId('job_10')
    job_10 = Job(job_id_10, task)
    job_10.creation_date = job_10.creation_date + timedelta(seconds=100)
    job_id_11 = JobId('job_11')
    job_11 = Job(job_id_11, task)
    job_11.creation_date = job_11.creation_date + timedelta(seconds=110)
    job_id_12 = JobId('job_12')
    job_12 = Job(job_id_12, task)
    job_12.creation_date = job_12.creation_date + timedelta(seconds=120)
    job_id_13 = JobId('job_13')
    job_13 = Job(job_id_13, task)
    job_13.creation_date = job_13.creation_date + timedelta(seconds=130)
    job_id_14 = JobId('job_14')
    job_14 = Job(job_id_14, task)
    job_14.creation_date = job_14.creation_date + timedelta(seconds=140)
    job_id_15 = JobId('job_15')
    job_15 = Job(job_id_15, task_locked)
    job_15.creation_date = job_15.creation_date + timedelta(seconds=150)
    job_id_16 = JobId('job_16')
    job_16 = Job(job_id_16, task_locked)
    job_16.creation_date = job_16.creation_date + timedelta(seconds=160)

    _JobManager._set(job_1)
    _JobManager._set(job_2)
    _JobManager._set(job_3)
    _JobManager._set(job_4)
    _JobManager._set(job_5)
    _JobManager._set(job_6)
    _JobManager._set(job_7)
    _JobManager._set(job_8)
    _JobManager._set(job_9)
    _JobManager._set(job_10)
    _JobManager._set(job_11)
    _JobManager._set(job_12)
    _JobManager._set(job_13)
    _JobManager._set(job_14)
    _JobManager._set(job_15)
    _JobManager._set(job_16)

    job_1.blocked()
    job_2.blocked()
    # job_3 -> submitted
    # job_4 -> submitted
    job_5.skipped()
    job_6.skipped()
    job_7.cancelled()
    job_8.cancelled()
    job_9.completed()
    job_10.completed()
    job_11.pending()
    job_12.pending()
    job_13.running()
    job_14.running()
    job_15.blocked()

    assert job_1.status == Status.BLOCKED
    assert job_2.status == Status.BLOCKED
    assert job_3.status == Status.SUBMITTED
    assert job_4.status == Status.SUBMITTED
    assert job_5.status == Status.SKIPPED
    assert job_6.status == Status.SKIPPED
    assert job_7.status == Status.CANCELLED
    assert job_8.status == Status.CANCELLED
    assert job_9.status == Status.COMPLETED
    assert job_10.status == Status.COMPLETED
    assert job_11.status == Status.PENDING
    assert job_12.status == Status.PENDING
    assert job_13.status == Status.RUNNING
    assert job_14.status == Status.RUNNING
    assert job_15.status == Status.BLOCKED
    assert job_16.status == Status.SUBMITTED

    assert len(_Scheduler.blocked_jobs) == 0
    assert _Scheduler.jobs_to_run.empty()

    res = _Scheduler._recover_jobs()
    print('-- status: ', [job.status for job in res])
    expected_order_job_executed_1 = ['job_11', 'job_12', 'job_13', 'job_14', 'job_1',
                                     'job_2', 'job_3', 'job_4', 'job_15', 'job_16']
    assert len(res) == 10
    assert [job.id for job in res] == expected_order_job_executed_1
    assert [job.status for job in res[:-2]] == [Status.COMPLETED for _ in range(8)]
    assert [job.status for job in res[-2:]] == [Status.BLOCKED for _ in range(2)]
    assert len(_Scheduler.blocked_jobs) == 2
    assert _Scheduler.jobs_to_run.empty()

    _Scheduler.blocked_jobs = []
    dn_inp_locked.unlock_edition()
    res = _Scheduler._recover_jobs()

    expected_order_job_executed_2 = ['job_15', 'job_16']
    assert len(res) == 2
    assert [job.id for job in res] == expected_order_job_executed_2
    assert [job.status for job in res] == [Status.COMPLETED for _ in range(2)]

    assert len(_Scheduler.blocked_jobs) == 0
    assert _Scheduler.jobs_to_run.empty()
