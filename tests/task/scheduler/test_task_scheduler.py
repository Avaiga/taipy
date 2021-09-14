from taipy.data.data_source import EmbeddedDataSource, DataSource
from taipy.task import Task
from taipy.task.scheduler import TaskScheduler


def mult(nb1: DataSource, nb2: DataSource):
    return nb1.get(None) * nb2.get(None)


def test_scheduled_task():
    task_scheduler = TaskScheduler()
    input_ds = [
        EmbeddedDataSource("input1", 0, None, {
            'data': 21
        }),
        EmbeddedDataSource("input2", 0, None, {
            'data': 2
        }),
    ]
    output_ds = [
        EmbeddedDataSource("output1", 0, None, {'data': 0})
    ]
    task = Task.create_task(
        "task1",
        input_data_sources=input_ds,
        function=mult,
        output_data_sources=output_ds
    )
    task_scheduler.submit(task)
    assert output_ds[0].get(None) == 42
