from typing import Dict, List
import requests
import json


session = requests.session()
BASE_URL = "http://0.0.0.0:5000/api/v1"

def compare(expected: Dict, output: Dict) -> List[str]:
    errors = []
    for k, v in expected.items():
        if k not in output:
            errors.append(f"key {k} not found in output")
        if v != output[k]:
            errors.append(f"key {k} has value {output[k]} instead of {v}")
    return errors

# Create Scenario: Should also create all of its dependencies(pipelines, tasks, datanodes, etc)
response = session.post(f"{BASE_URL}/scenarios?config_name=scenario_cfg")
assert response.status_code == 201

scenarios = session.get(f"{BASE_URL}/scenarios").json()

# Pipelines

pipeline_ids = scenarios[0].get("pipeline_ids")
pipeline = session.get(f"{BASE_URL}/pipelines/{pipeline_ids[0]}").json()

pipeline_erros = compare(json.load(open("tests/end_to_end/json/expected/pipeline.json")), pipeline)

assert pipeline_erros == []

# Datanode

# Task

# Job

# Pipeline

# Scenario

# Cycle
