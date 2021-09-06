from taipy.task import Task


def test_create_task():
    task = Task.create_task("name_1", [], print, [])
    assert task.id is not None
