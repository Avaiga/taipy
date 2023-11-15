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


def test_get_scenario(client, default_scenario):
    # test 404
    user_url = url_for("api.scenario_by_id", scenario_id="foo")
    rep = client.get(user_url)
    assert rep.status_code == 404

    with mock.patch("taipy.core.scenario._scenario_manager._ScenarioManager._get") as manager_mock:
        manager_mock.return_value = default_scenario

        # test get_scenario
        rep = client.get(url_for("api.scenario_by_id", scenario_id="foo"))
        assert rep.status_code == 200


def test_delete_scenario(client):
    # test 404
    user_url = url_for("api.scenario_by_id", scenario_id="foo")
    rep = client.get(user_url)
    assert rep.status_code == 404

    with mock.patch("taipy.core.scenario._scenario_manager._ScenarioManager._delete"), mock.patch(
        "taipy.core.scenario._scenario_manager._ScenarioManager._get"
    ):
        # test get_scenario
        rep = client.delete(url_for("api.scenario_by_id", scenario_id="foo"))
        assert rep.status_code == 200


def test_create_scenario(client, default_scenario_config):
    # without config param
    scenarios_url = url_for("api.scenarios")
    rep = client.post(scenarios_url)
    assert rep.status_code == 400

    # config does not exist
    scenarios_url = url_for("api.scenarios", config_id="foo")
    rep = client.post(scenarios_url)
    assert rep.status_code == 404

    with mock.patch("src.taipy.rest.api.resources.scenario.ScenarioList.fetch_config") as config_mock:
        config_mock.return_value = default_scenario_config
        scenarios_url = url_for("api.scenarios", config_id="bar")
        rep = client.post(scenarios_url)
        assert rep.status_code == 201


def test_get_all_scenarios(client, default_sequence, default_scenario_config_list):
    for ds in range(10):
        with mock.patch("src.taipy.rest.api.resources.scenario.ScenarioList.fetch_config") as config_mock:
            config_mock.return_value = default_scenario_config_list[ds]
            scenarios_url = url_for("api.scenarios", config_id=config_mock.name)
            client.post(scenarios_url)

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

    with mock.patch("taipy.core.scenario._scenario_manager._ScenarioManager._get") as manager_mock:
        manager_mock.return_value = default_scenario

        # test get_scenario
        rep = client.post(url_for("api.scenario_submit", scenario_id="foo"))
        assert rep.status_code == 200
