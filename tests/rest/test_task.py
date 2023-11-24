# Copyright 2023 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

from unittest import mock

from flask import url_for


def test_get_task(client, default_task):
    # test 404
    user_url = url_for("api.task_by_id", task_id="foo")
    rep = client.get(user_url)
    assert rep.status_code == 404

    with mock.patch("taipy.core.task._task_manager._TaskManager._get") as manager_mock:
        manager_mock.return_value = default_task

        # test get_task
        rep = client.get(url_for("api.task_by_id", task_id="foo"))
        assert rep.status_code == 200


def test_delete_task(client):
    # test 404
    user_url = url_for("api.task_by_id", task_id="foo")
    rep = client.get(user_url)
    assert rep.status_code == 404

    with mock.patch("taipy.core.task._task_manager._TaskManager._delete"), mock.patch(
        "taipy.core.task._task_manager._TaskManager._get"
    ):
        # test get_task
        rep = client.delete(url_for("api.task_by_id", task_id="foo"))
        assert rep.status_code == 200


def test_create_task(client, default_task_config):
    # without config param
    tasks_url = url_for("api.tasks")
    rep = client.post(tasks_url)
    assert rep.status_code == 400

    # config does not exist
    tasks_url = url_for("api.tasks", config_id="foo")
    rep = client.post(tasks_url)
    assert rep.status_code == 404

    with mock.patch("src.taipy.rest.api.resources.task.TaskList.fetch_config") as config_mock:
        config_mock.return_value = default_task_config
        tasks_url = url_for("api.tasks", config_id="bar")
        rep = client.post(tasks_url)
        assert rep.status_code == 201


def test_get_all_tasks(client, task_data, default_task_config_list):
    for ds in range(10):
        with mock.patch("src.taipy.rest.api.resources.task.TaskList.fetch_config") as config_mock:
            config_mock.return_value = default_task_config_list[ds]
            tasks_url = url_for("api.tasks", config_id=config_mock.name)
            client.post(tasks_url)

    rep = client.get(tasks_url)
    assert rep.status_code == 200

    results = rep.get_json()
    assert len(results) == 10


def test_execute_task(client, default_task):
    # test 404
    user_url = url_for("api.task_submit", task_id="foo")
    rep = client.post(user_url)
    assert rep.status_code == 404

    with mock.patch("taipy.core.task._task_manager._TaskManager._get") as manager_mock:
        manager_mock.return_value = default_task

        # test get_task
        rep = client.post(url_for("api.task_submit", task_id="foo"))
        assert rep.status_code == 200
