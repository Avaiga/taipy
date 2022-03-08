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

    with mock.patch("taipy.core.job._job_manager._JobManager._delete"):
        # test get_job
        rep = client.delete(url_for("api.job_by_id", job_id="foo"))
        assert rep.status_code == 200


def test_create_job(client, default_task_config):
    # without config param
    jobs_url = url_for("api.jobs")
    data = {"bad": "data"}
    rep = client.post(jobs_url, json=data)
    assert rep.status_code == 400

    with mock.patch(
        "src.taipy.rest.api.resources.job.JobList.fetch_config"
    ) as config_mock:
        config_mock.return_value = default_task_config
        rep = client.post(jobs_url, json={"task_name": "foo"})
        assert rep.status_code == 201


def test_get_all_jobs(client, create_job_list):
    jobs_url = url_for("api.jobs")
    rep = client.get(jobs_url)
    assert rep.status_code == 200

    results = rep.get_json()
    assert len(results) == 10
