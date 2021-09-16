from taipy.data.data_source import DataSourceEntity, EmbeddedDataSourceEntity
from taipy.data.data_source.models import Scope
from taipy.task import Task, TaskEntity
from taipy.task.scheduler import TaskScheduler


def mult(nb1: DataSourceEntity, nb2: DataSourceEntity):
    return nb1.get(None) * nb2.get(None)


def test_scheduled_task():
    task_scheduler = TaskScheduler()
    input_ds = [
        EmbeddedDataSourceEntity.create("input1", Scope.PIPELINE, "i1", data=21),
        EmbeddedDataSourceEntity.create("input2", Scope.PIPELINE, "i2", data=2),
    ]
    output_ds = [
        EmbeddedDataSourceEntity.create("output1", Scope.PIPELINE, "o1", data=0)
    ]
    task = TaskEntity(
        "task1",
        input=input_ds,
        function=mult,
        output=output_ds,
    )
    task_scheduler.submit(task)
    assert output_ds[0].get(None) == 42
