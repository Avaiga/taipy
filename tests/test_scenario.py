from unittest import mock

import pytest
from flask import url_for


def test_get_scenario(client, default_scenario):
    # test 404
    user_url = url_for("api.scenario_by_id", scenario_id="foo")
    rep = client.get(user_url)
    assert rep.status_code == 404

    with mock.patch(
        "taipy.scenario.manager.scenario_manager.ScenarioManager.get"
    ) as manager_mock:
        manager_mock.return_value = default_scenario

        # test get_scenario
        rep = client.get(url_for("api.scenario_by_id", scenario_id="foo"))
        assert rep.status_code == 200


def test_delete_scenario(client):
    # test 404
    user_url = url_for("api.scenario_by_id", scenario_id="foo")
    rep = client.get(user_url)
    assert rep.status_code == 404

    with mock.patch("taipy.scenario.manager.scenario_manager.ScenarioManager.delete"):
        # test get_scenario
        rep = client.delete(url_for("api.scenario_by_id", scenario_id="foo"))
        assert rep.status_code == 200


def test_create_scenario(client, scenario_data, default_pipeline):
    # test bad data
    scenarios_url = url_for("api.scenarios")
    data = {"bad": "data"}
    rep = client.post(scenarios_url, json=data)
    assert rep.status_code == 400

    with mock.patch(
        "taipy.pipeline.manager.pipeline_manager.PipelineManager.get"
    ) as manager_mock:
        manager_mock.return_value = default_pipeline

        rep = client.post(scenarios_url, json=scenario_data)
        assert rep.status_code == 201


def test_get_all_scenarios(client, scenario_data, default_pipeline):
    scenarios_url = url_for("api.scenarios")

    with mock.patch(
        "taipy.pipeline.manager.pipeline_manager.PipelineManager.get"
    ) as manager_mock:
        manager_mock.return_value = default_pipeline

        for ds in range(10):
            client.post(scenarios_url, json=scenario_data)

        rep = client.get(scenarios_url)
        assert rep.status_code == 200

        results = rep.get_json()
        assert len(results) == 10


@pytest.mark.xfail()
def test_execute_scenario(client, default_scenario):
    # test 404
    user_url = url_for("api.scenario_submit", scenario_id="foo")
    rep = client.post(user_url)
    assert rep.status_code == 404

    with mock.patch(
        "taipy.scenario.manager.scenario_manager.ScenarioManager.get"
    ) as manager_mock:
        manager_mock.return_value = default_scenario

        # test get_scenario
        rep = client.post(url_for("api.scenario_submit", scenario_id="foo"))
        assert rep.status_code == 200
