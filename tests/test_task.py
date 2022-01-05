from unittest import mock

from flask import url_for


def test_get_task(client, default_task):
    # test 404
    user_url = url_for("api.task_by_id", task_id="foo")
    rep = client.get(user_url)
    assert rep.status_code == 404

    with mock.patch("taipy.task.manager.task_manager.TaskManager.get") as manager_mock:
        manager_mock.return_value = default_task

        # test get_task
        rep = client.get(url_for("api.task_by_id", task_id="foo"))
        assert rep.status_code == 200


def test_delete_task(client):
    # test 404
    user_url = url_for("api.task_by_id", task_id="foo")
    rep = client.get(user_url)
    assert rep.status_code == 404

    with mock.patch("taipy.task.manager.task_manager.TaskManager.delete"):
        # test get_task
        rep = client.delete(url_for("api.task_by_id", task_id="foo"))
        assert rep.status_code == 200


def test_create_task(client, task_data, default_datasource):
    # test bad data
    tasks_url = url_for("api.tasks")
    data = {"bad": "data"}
    rep = client.post(tasks_url, json=data)
    assert rep.status_code == 400

    with mock.patch("taipy.data.manager.data_manager.DataManager.get") as manager_mock:
        manager_mock.return_value = default_datasource

        rep = client.post(tasks_url, json=task_data)
        assert rep.status_code == 201


def test_get_all_tasks(client, task_data, default_datasource):
    tasks_url = url_for("api.tasks")

    with mock.patch("taipy.data.manager.data_manager.DataManager.get") as manager_mock:
        manager_mock.return_value = default_datasource

        for ds in range(10):
            client.post(tasks_url, json=task_data)

        rep = client.get(tasks_url)
        assert rep.status_code == 200

        results = rep.get_json()
        assert len(results) == 10


def test_execute_task(client, default_task):
    # test 404
    user_url = url_for("api.task_submit", task_id="foo")
    rep = client.post(user_url)
    assert rep.status_code == 404

    with mock.patch("taipy.task.manager.task_manager.TaskManager.get") as manager_mock:
        manager_mock.return_value = default_task

        # test get_task
        rep = client.post(url_for("api.task_submit", task_id="foo"))
        assert rep.status_code == 200
