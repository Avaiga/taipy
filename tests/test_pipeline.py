from unittest import mock

import pytest
from flask import url_for


def test_get_pipeline(client, default_pipeline):
    # test 404
    user_url = url_for("api.pipeline_by_id", pipeline_id="foo")
    rep = client.get(user_url)
    assert rep.status_code == 404

    with mock.patch(
        "taipy.pipeline.manager.pipeline_manager.PipelineManager.get"
    ) as manager_mock:
        manager_mock.return_value = default_pipeline

        # test get_pipeline
        rep = client.get(url_for("api.pipeline_by_id", pipeline_id="foo"))
        assert rep.status_code == 200


def test_delete_pipeline(client):
    # test 404
    user_url = url_for("api.pipeline_by_id", pipeline_id="foo")
    rep = client.get(user_url)
    assert rep.status_code == 404

    with mock.patch("taipy.pipeline.manager.pipeline_manager.PipelineManager.delete"):
        # test get_pipeline
        rep = client.delete(url_for("api.pipeline_by_id", pipeline_id="foo"))
        assert rep.status_code == 200


def test_create_pipeline(client, pipeline_data, default_task):
    # test bad data
    pipelines_url = url_for("api.pipelines")
    data = {"bad": "data"}
    rep = client.post(pipelines_url, json=data)
    assert rep.status_code == 400

    with mock.patch("taipy.task.manager.task_manager.TaskManager.get") as manager_mock:
        manager_mock.return_value = default_task

        rep = client.post(pipelines_url, json=pipeline_data)
        assert rep.status_code == 201


def test_get_all_pipelines(client, pipeline_data, default_task):
    pipelines_url = url_for("api.pipelines")

    with mock.patch("taipy.task.manager.task_manager.TaskManager.get") as manager_mock:
        manager_mock.return_value = default_task

        for ds in range(10):
            client.post(pipelines_url, json=pipeline_data)

        rep = client.get(pipelines_url)
        assert rep.status_code == 200

        results = rep.get_json()
        assert len(results) == 10


@pytest.mark.xfail()
def test_execute_pipeline(client, default_pipeline):
    # test 404
    user_url = url_for("api.pipeline_submit", pipeline_id="foo")
    rep = client.post(user_url)
    assert rep.status_code == 404

    with mock.patch(
        "taipy.pipeline.manager.pipeline_manager.PipelineManager.get"
    ) as manager_mock:
        manager_mock.return_value = default_pipeline

        # test get_pipeline
        rep = client.post(url_for("api.pipeline_submit", pipeline_id="foo"))
        assert rep.status_code == 200
