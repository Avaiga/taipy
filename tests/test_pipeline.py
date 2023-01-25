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

import pytest
from flask import url_for


def test_get_pipeline(client, default_pipeline):
    # test 404
    user_url = url_for("api.pipeline_by_id", pipeline_id="foo")
    rep = client.get(user_url)
    assert rep.status_code == 404

    with mock.patch("taipy.core.pipeline._pipeline_manager._PipelineManager._get") as manager_mock:
        manager_mock.return_value = default_pipeline

        # test get_pipeline
        rep = client.get(url_for("api.pipeline_by_id", pipeline_id="foo"))
        assert rep.status_code == 200


def test_delete_pipeline(client):
    # test 404
    user_url = url_for("api.pipeline_by_id", pipeline_id="foo")
    rep = client.get(user_url)
    assert rep.status_code == 404

    with mock.patch("taipy.core.pipeline._pipeline_manager._PipelineManager._delete"), mock.patch(
        "taipy.core.pipeline._pipeline_manager._PipelineManager._get"
    ):
        # test get_pipeline
        rep = client.delete(url_for("api.pipeline_by_id", pipeline_id="foo"))
        assert rep.status_code == 200


def test_create_pipeline(client, default_pipeline_config):
    # without config param
    pipelines_url = url_for("api.pipelines")
    rep = client.post(pipelines_url)
    assert rep.status_code == 400

    # config does not exist
    pipelines_url = url_for("api.pipelines", config_id="foo")
    rep = client.post(pipelines_url)
    assert rep.status_code == 404

    with mock.patch("src.taipy.rest.api.resources.pipeline.PipelineList.fetch_config") as config_mock:
        config_mock.return_value = default_pipeline_config
        pipelines_url = url_for("api.pipelines", config_id="bar")
        rep = client.post(pipelines_url)
        assert rep.status_code == 201


def test_get_all_pipelines(client, default_pipeline_config_list):
    for ds in range(10):
        with mock.patch("src.taipy.rest.api.resources.pipeline.PipelineList.fetch_config") as config_mock:
            config_mock.return_value = default_pipeline_config_list[ds]
            pipelines_url = url_for("api.pipelines", config_id=config_mock.name)
            client.post(pipelines_url)

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

    with mock.patch("taipy.core.pipeline._pipeline_manager._PipelineManager._get") as manager_mock:
        manager_mock.return_value = default_pipeline

        # test get_pipeline
        rep = client.post(url_for("api.pipeline_submit", pipeline_id="foo"))
        assert rep.status_code == 200
