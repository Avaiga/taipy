from taipy.task import TaskEntity, Task


def test_create_task_entity():
    task = TaskEntity("namE 1", [], print, [])
    assert task.name == "name_1"
    assert task.id is not None

def test_create_task():
    task = Task("namE 1 ", [], print, [])
    assert task.name == "name_1"
