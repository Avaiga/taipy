# Copyright 2022 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import json
from typing import Dict

from flask import url_for


def create_and_submit_scenario(config_id: str, client) -> Dict:
    response = client.post(url_for("api.scenarios", config_id=config_id))
    assert response.status_code == 201

    scenario = response.json.get("scenario")
    assert (set(scenario) - set(json.load(open("tests/json/expected/scenario.json")))) == set()

    response = client.post(url_for("api.scenario_submit", scenario_id=scenario.get("id")))
    assert response.status_code == 200

    return scenario


def get(url, name, client) -> Dict:
    response = client.get(url)
    returned_data = response.json.get(name)

    assert (set(returned_data) - set(json.load(open(f"tests/json/expected/{name}.json")))) == set()

    return returned_data


def get_all(url, expected_quantity, client):
    response = client.get(url)

    assert len(response.json) == expected_quantity


def delete(url, client):
    response = client.delete(url)

    assert response.status_code == 200


def test_end_to_end(client, setup_end_to_end):
    # Create Scenario: Should also create all of its dependencies(pipelines, tasks, datanodes, etc)
    scenario = create_and_submit_scenario("scenario", client)

    # Get other models and verify if they return the necessary fields
    cycle = get(url_for("api.cycle_by_id", cycle_id=scenario.get("cycle")), "cycle", client)
    pipeline = get(
        url_for("api.pipeline_by_id", pipeline_id=scenario.get("pipelines")[0]),
        "pipeline",
        client,
    )
    task = get(url_for("api.task_by_id", task_id=pipeline.get("tasks")[0]), "task", client)
    datanode = get(
        url_for("api.datanode_by_id", datanode_id=task.get("input_ids")[0]),
        "datanode",
        client,
    )

    # Get All
    get_all(url_for("api.scenarios"), 1, client)
    get_all(url_for("api.cycles"), 1, client)
    get_all(url_for("api.pipelines"), 1, client)
    get_all(url_for("api.tasks"), 2, client)
    get_all(url_for("api.datanodes"), 5, client)
    get_all(url_for("api.jobs"), 2, client)

    # Delete entities
    delete(url_for("api.cycle_by_id", cycle_id=cycle.get("id")), client)
    delete(url_for("api.pipeline_by_id", pipeline_id=pipeline.get("id")), client)
    delete(url_for("api.task_by_id", task_id=task.get("id")), client)
    delete(url_for("api.datanode_by_id", datanode_id=datanode.get("id")), client)
