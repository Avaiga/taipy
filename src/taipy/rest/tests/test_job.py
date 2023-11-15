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


def test_get_job(client, default_job):
    # test 404
    user_url = url_for("api.job_by_id", job_id="foo")
    rep = client.get(user_url)
    assert rep.status_code == 404

    with mock.patch("taipy.core.job._job_manager._JobManager._get") as manager_mock:
        manager_mock.return_value = default_job

        # test get_job
        rep = client.get(url_for("api.job_by_id", job_id="foo"))
        assert rep.status_code == 200


def test_delete_job(client):
    # test 404
    user_url = url_for("api.job_by_id", job_id="foo")
    rep = client.get(user_url)
    assert rep.status_code == 404

    with mock.patch("taipy.core.job._job_manager._JobManager._delete"), mock.patch(
        "taipy.core.job._job_manager._JobManager._get"
    ):
        # test get_job
        rep = client.delete(url_for("api.job_by_id", job_id="foo"))
        assert rep.status_code == 200


def test_create_job(client, default_task_config):
    # without config param
    jobs_url = url_for("api.jobs")
    rep = client.post(jobs_url)
    assert rep.status_code == 400

    with mock.patch("src.taipy.rest.api.resources.job.JobList.fetch_config") as config_mock:
        config_mock.return_value = default_task_config
        jobs_url = url_for("api.jobs", task_id="foo")
        rep = client.post(jobs_url)
        assert rep.status_code == 201


def test_get_all_jobs(client, create_job_list):
    jobs_url = url_for("api.jobs")
    rep = client.get(jobs_url)
    assert rep.status_code == 200

    results = rep.get_json()
    assert len(results) == 10


def test_cancel_job(client, default_job):
    # test 404
    from taipy.core._orchestrator._orchestrator_factory import _OrchestratorFactory

    _OrchestratorFactory._build_orchestrator()
    _OrchestratorFactory._build_dispatcher()

    user_url = url_for("api.job_cancel", job_id="foo")
    rep = client.post(user_url)
    assert rep.status_code == 404

    with mock.patch("taipy.core.job._job_manager._JobManager._get") as manager_mock:
        manager_mock.return_value = default_job

        # test get_job
        rep = client.post(url_for("api.job_cancel", job_id="foo"))
        assert rep.status_code == 200
