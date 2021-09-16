from taipy.task import TaskEntity


def test_create_task():
    task = TaskEntity("name_1", [], print, [])
    assert task.id is not None
