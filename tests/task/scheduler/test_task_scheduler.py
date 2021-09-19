import uuid
from concurrent.futures import Future
from time import sleep
from typing import Optional

from taipy.data.entity import EmbeddedDataSourceEntity
from taipy.data.data_source_entity import DataSourceEntity
from taipy.data.scope import Scope
from taipy.task import TaskEntity
from taipy.task.scheduler import TaskScheduler


def mult(nb1: DataSourceEntity, nb2: DataSourceEntity):
    return nb1.get(None) * nb2.get(None)


class WaitingMult:
    """
    This class emulates a time-consuming calculation task
    The TaskScheduler will call the `__call__` function which will block until the main thread calls the `unblock` method
    """
    def __init__(self):
        self._nb1: Optional[DataSourceEntity] = None
        self._nb2: Optional[DataSourceEntity] = None
        self.future = Future()

    def __call__(self, nb1: DataSourceEntity, nb2: DataSourceEntity):
        self._nb1 = nb1
        self._nb2 = nb2
        return self.future.result()

    def unblock(self):
        self.future.set_result(
            self._nb1.get(None) * self._nb2.get(None)
        )
        sleep(0.1)  # Wait end of callback


def test_scheduled_task():
    task_scheduler = TaskScheduler()
    task = _create_task(mult)

    task_scheduler.submit(task)
    assert task.output[0].get(None) == 42


def test_scheduled_task_multithreading():
    task_scheduler = TaskScheduler(parallel_execution=True)
    sleep_mult = WaitingMult()
    task = _create_task(sleep_mult)

    task_scheduler.submit(task)
    assert task.output[0].get(None) == 0

    sleep_mult.unblock()
    assert task.output[0].get(None) == 42


def test_scheduled_task_multithreading_multiple_task():
    task_scheduler = TaskScheduler(parallel_execution=True)

    sleep_mult_1 = WaitingMult()
    sleep_mult_2 = WaitingMult()

    task_1 = _create_task(sleep_mult_1)
    task_scheduler.submit(task_1)

    task_2 = _create_task(sleep_mult_2)
    task_scheduler.submit(task_2)

    assert task_1.output[0].get(None) == 0
    assert task_2.output[0].get(None) == 0

    sleep_mult_2.unblock()
    assert task_1.output[0].get(None) == 0
    assert task_2.output[0].get(None) == 42

    sleep_mult_1.unblock()
    assert task_1.output[0].get(None) == 42
    assert task_2.output[0].get(None) == 42


def _create_task(function):
    task_name = str(uuid.uuid4())
    output_name = str(uuid.uuid4())
    input_ds = [
        EmbeddedDataSourceEntity.create("input1", Scope.PIPELINE, "i1", data=21),
        EmbeddedDataSourceEntity.create("input2", Scope.PIPELINE, "i2", data=2),
    ]
    output_ds = [
        EmbeddedDataSourceEntity.create(output_name, Scope.PIPELINE, "o1", data=0)
    ]
    return TaskEntity(
        task_name,
        input=input_ds,
        function=function,
        output=output_ds,
    )
