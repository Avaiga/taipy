# Copyright 2021-2024 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

from flask import request
from flask_restful import Resource

from taipy.common.config import Config
from taipy.core import Scenario
from taipy.core.exceptions.exceptions import NonExistingScenario, NonExistingScenarioConfig
from taipy.core.scenario._scenario_manager_factory import _ScenarioManagerFactory

from ...commons.to_from_model import _to_model
from ..exceptions.exceptions import ConfigIdMissingException
from ..middlewares._middleware import _middleware
from ..schemas import ScenarioResponseSchema


def _get_or_raise(scenario_id: str) -> Scenario:
    if scenario := _ScenarioManagerFactory._build_manager()._get(scenario_id):
        return scenario

    raise NonExistingScenario(scenario_id)


REPOSITORY = "scenario"


class ScenarioResource(Resource):
    """Single object resource

    ---
    get:
      tags:
        - api
      description: |
        Returns a `ScenarioSchema^` representing the unique scenario identified by *scenario_id*. If no scenario
        corresponds to *scenario_id*, a `404` error is returned.

        !!! Example

            === "Curl"
                ```shell
                    curl -X GET http://localhost:5000/api/v1/scenarios/SCENARIO_63cb358d-5834-4d73-84e4-a6343df5e08c
                ```
                In this example the REST API is served on port 5000 on localhost. We are using curl command line
                client.

                `SCENARIO_63cb358d-5834-4d73-84e4-a6343df5e08c` is the value of the *scenario_id* parameter. It
                represents the identifier of the Scenario we want to retrieve.

                In case of success here is an example of the response:
                ``` JSON
                {"scenario": {
                    "cycle": "CYCLE_863418_fdd1499a-8925-4540-93fd-9dbfb4f0846d",
                    "id": "SCENARIO_63cb358d-5834-4d73-84e4-a6343df5e08c",
                    "properties": {},
                    "tags": [],
                    "version": "latest",
                    "sequences": [
                        "SEQUENCE_mean_baseline_5af317c9-34df-48b4-8a8a-bf4007e1de99",
                        "SEQUENCE_arima_90aef6b9-8922-4a0c-b625-b2c6f3d19fa4"],
                    "subscribers": [],
                    "creation_date": "2022-08-15T19:21:01.871587",
                    "primary_scenario": true}}
                ```

                In case of failure here is an example of the response:
                ``` JSON
                {"message": "SCENARIO_63cb358d-5834-4d73-84e4-a6343df5e08c not found."}
                ```

            === "Python"
                This Python example requires the 'requests' package to be installed (`pip install requests`).
                ```python
                import requests
                response = requests.get(
                    "http://localhost:5000/api/v1/scenarios/SCENARIO_63cb358d-5834-4d73-84e4-a6343df5e08c"
                )
                print(response)
                print(response.json())
                ```
                `SCENARIO_63cb358d-5834-4d73-84e4-a6343df5e08c` is the value of the  *scenario_id* parameter. It
                represents the identifier of the Cycle we want to retrieve.

                In case of success here is an output example:
                ```
                <Response [200]>
                {"scenario": {
                    "cycle": "CYCLE_863418_fdd1499a-8925-4540-93fd-9dbfb4f0846d",
                    "id": "SCENARIO_63cb358d-5834-4d73-84e4-a6343df5e08c",
                    "properties": {},
                    "tags": [],
                    "version": "latest",
                    "sequences": [
                        "SEQUENCE_mean_baseline_5af317c9-34df-48b4-8a8a-bf4007e1de99",
                        "SEQUENCE_arima_90aef6b9-8922-4a0c-b625-b2c6f3d19fa4"],
                    "subscribers": [],
                    "creation_date": "2022-08-15T19:21:01.871587",
                    "primary_scenario": true}}
                ```

                In case of failure here is an output example:
                ```
                <Response [404]>
                {'message': 'Scenario SCENARIO_63cb358d-5834-4d73-84e4-a6343df5e08c not found.'}

                ```

        !!! Note
            When the authorization feature is activated (available in Taipy Enterprise edition only), this endpoint
            requires the `TAIPY_READER` role.

        parameters:
        - in: path
          name: scenario_id
          schema:
            type: string
          description: The identifier of the scenario to retrieve.
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  scenario: ScenarioSchema
        404:
          description: No scenario has the *scenario_id* identifier.
    delete:
      tags:
        - api
      description: |
        Delete the `Scenario^` scenario identified by the *scenario_id* given as parameter. If the scenario does not
        exist, a 404 error is returned.

        !!! Example

            === "Curl"
                ```shell
                    curl -X DELETE http://localhost:5000/api/v1/scenarios/SCENARIO_63cb358d-5834-4d73-84e4-a6343df5e08c
                ```
                In this example the REST API is served on port 5000 on localhost. We are using curl command line
                client.

                `SCENARIO_63cb358d-5834-4d73-84e4-a6343df5e08c` is the value of the  *scenario_id* parameter. It
                represents the identifier of the scenario we want to delete.

                In case of success here is an example of the response:
                ``` JSON
                {"msg": "Scenario SCENARIO_63cb358d-5834-4d73-84e4-a6343df5e08c deleted."}
                ```

                In case of failure here is an example of the response:
                ``` JSON
                {"message": "Scenario SCENARIO_63cb358d-5834-4d73-84e4-a6343df5e08c not found."}
                ```

            === "Python"
                This Python example requires the 'requests' package to be installed (`pip install requests`).
                ```python
                import requests
                response = requests.delete(
                    "http://localhost:5000/api/v1/scenarios/SCENARIO_63cb358d-5834-4d73-84e4-a6343df5e08c"
                )
                print(response)
                print(response.json())
                ```
                `SCENARIO_63cb358d-5834-4d73-84e4-a6343df5e08c` is the value of the *scenario_id* parameter. It
                represents the identifier of the Scenario we want to delete.

                In case of success here is an output example:
                ```
                <Response [200]>
                {"msg": "Scenario SCENARIO_63cb358d-5834-4d73-84e4-a6343df5e08c deleted."}
                ```

                In case of failure here is an output example:
                ```
                <Response [404]>
                {'message': 'Scenario SCENARIO_63cb358d-5834-4d73-84e4-a6343df5e08c not found.'}

                ```

        !!! Note
            When the authorization feature is activated (available in Taipy Enterprise edition only), this endpoint
            requires the `TAIPY_EDITOR` role.

      parameters:
        - in: path
          name: scenario_id
          schema:
            type: string
          description: The identifier of the scenario to delete.
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
                    description: Status message.
        404:
          description: No scenario has the *scenario_id* identifier.
    """

    def __init__(self, **kwargs):
        self.logger = kwargs.get("logger")

    @_middleware
    def get(self, scenario_id):
        schema = ScenarioResponseSchema()
        scenario = _get_or_raise(scenario_id)
        return {"scenario": schema.dump(_to_model(REPOSITORY, scenario))}

    @_middleware
    def delete(self, scenario_id):
        manager = _ScenarioManagerFactory._build_manager()
        _get_or_raise(scenario_id)
        manager._delete(scenario_id)
        return {"message": f"Scenario {scenario_id} was deleted."}


class ScenarioList(Resource):
    """Creation and get_all

    ---
    get:
      tags:
        - api
      summary: Get all scenarios.
      description: |
        Returns a `ScenarioSchema^` list representing all existing Scenarios.

        !!! Example

            === "Curl"
                ```shell
                    curl -X GET http://localhost:5000/api/v1/scenarios
                ```
                In this example the REST API is served on port 5000 on localhost. We are using curl command line
                client.

                Here is an example of the response:
                ``` JSON
                [{
                    "cycle": "CYCLE_863418_fdd1499a-8925-4540-93fd-9dbfb4f0846d",
                    "id": "SCENARIO_63cb358d-5834-4d73-84e4-a6343df5e08c",
                    "properties": {},
                    "tags": [],
                    "version": "latest",
                    "sequences": [
                        "SEQUENCE_mean_baseline_5af317c9-34df-48b4-8a8a-bf4007e1de99",
                        "SEQUENCE_arima_90aef6b9-8922-4a0c-b625-b2c6f3d19fa4"],
                    "subscribers": [],
                    "creation_date": "2022-08-15T19:21:01.871587",
                    "primary_scenario": true
                    }
                ]
                ```

                If there is no scenario, the response is an empty list as follows:
                ``` JSON
                []
                ```

            === "Python"
                This Python example requires the 'requests' package to be installed (`pip install requests`).
                ```python
                import requests
                response = requests.get("http://localhost:5000/api/v1/scenarios")
                print(response)
                print(response.json())
                ```

                In case of success here is an output example:
                ```
                <Response [200]>
                [{
                    "cycle": "CYCLE_863418_fdd1499a-8925-4540-93fd-9dbfb4f0846d",
                    "id": "SCENARIO_63cb358d-5834-4d73-84e4-a6343df5e08c",
                    "properties": {},
                    "tags": [],
                    "version": "latest",
                    "sequences": [
                        "SEQUENCE_mean_baseline_5af317c9-34df-48b4-8a8a-bf4007e1de99",
                        "SEQUENCE_arima_90aef6b9-8922-4a0c-b625-b2c6f3d19fa4"],
                    "subscribers": [],
                    "creation_date": "2022-08-15T19:21:01.871587",
                    "primary_scenario": true
                    }
                ]
                ```

                If there is no scenario, the response is an empty list as follows:
                ```
                <Response [200]>
                []
                ```

        !!! Note
            When the authorization feature is activated (available in Taipy Enterprise edition only), this endpoint
            requires the `TAIPY_READER` role.

      responses:
        200:
          content:
            application/json:
              schema:
                allOf:
                  - type: object
                    properties:
                      results:
                        type: array
                        items:
                          $ref: '#/components/schemas/ScenarioSchema'
    post:
      tags:
        - api
      description: |
        Creates a new scenario from the  *config_id*. If the config does not exist, a 404 error is returned.

        !!! Example

            === "Curl"
                ```shell
                    curl -X POST http://localhost:5000/api/v1/scenarios?config_id=my_scenario_config
                ```
                In this example the REST API is served on port 5000 on localhost. We are using curl command line
                client.

                In this example the *config_id* value ("my_scenario_config") is given as parameter directly in the
                url. A corresponding `ScenarioConfig^` must exist and must have been configured before.

                Here is the output message example:
                ```
                {"msg": "scenario created.",
                "scenario": {
                    "cycle": "CYCLE_863418_fdd1499a-8925-4540-93fd-9dbfb4f0846d",
                    "id": "SCENARIO_63cb358d-5834-4d73-84e4-a6343df5e08c",
                    "properties": {},
                    "tags": [],
                    "version": "latest",
                    "sequences": [
                        "SEQUENCE_mean_baseline_5af317c9-34df-48b4-8a8a-bf4007e1de99",
                        "SEQUENCE_arima_90aef6b9-8922-4a0c-b625-b2c6f3d19fa4"],
                    "subscribers": [],
                    "creation_date": "2022-08-15T19:21:01.871587",
                    "primary_scenario": true}
                }
                ```

            === "Python"
                This Python example requires the 'requests' package to be installed (`pip install requests`).
                ```python
                import requests
                response = requests.post("http://localhost:5000/api/v1/scenarios?config_id=my_scenario_config")
                print(response)
                print(response.json())
                ```
                In this example the *config_id* value ("my_scenario_config") is given as parameter directly in the
                url. A corresponding `ScenarioConfig^` must exist and must have been configured before.

                Here is the output example:
                ```
                <Response [201]>
                {"msg": "scenario created.",
                "scenario": {
                    "cycle": "CYCLE_863418_fdd1499a-8925-4540-93fd-9dbfb4f0846d",
                    "id": "SCENARIO_63cb358d-5834-4d73-84e4-a6343df5e08c",
                    "properties": {},
                    "tags": [],
                    "version": "latest",
                    "sequences": [
                        "SEQUENCE_mean_baseline_5af317c9-34df-48b4-8a8a-bf4007e1de99",
                        "SEQUENCE_arima_90aef6b9-8922-4a0c-b625-b2c6f3d19fa4"],
                    "subscribers": [],
                    "creation_date": "2022-08-15T19:21:01.871587",
                    "primary_scenario": true}
                }
                ```

        !!! Note
            When the authorization feature is activated (available in Taipy Enterprise edition only), this endpoint
            requires the `TAIPY_EDITOR` role.

      parameters:
        - in: query
          name: config_id
          schema:
            type: string
          description: The identifier of the scenario configuration.
      responses:
        201:
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
                    description: Status message.
                  scenario: ScenarioSchema
    """

    def __init__(self, **kwargs):
        self.logger = kwargs.get("logger")

    def fetch_config(self, config_id):
        if config := Config.scenarios.get(config_id):
            return config

        raise NonExistingScenarioConfig(config_id)

    @_middleware
    def get(self):
        schema = ScenarioResponseSchema(many=True)
        manager = _ScenarioManagerFactory._build_manager()
        scenarios = [_to_model(REPOSITORY, scenario) for scenario in manager._get_all()]
        return schema.dump(scenarios)

    @_middleware
    def post(self):
        args = request.args
        config_id = args.get("config_id")

        response_schema = ScenarioResponseSchema()
        manager = _ScenarioManagerFactory._build_manager()

        if not config_id:
            raise ConfigIdMissingException

        config = self.fetch_config(config_id)
        scenario = manager._create(config)

        return {
            "message": "Scenario was created.",
            "scenario": response_schema.dump(_to_model(REPOSITORY, scenario)),
        }, 201


class ScenarioExecutor(Resource):
    """Execute a scenario

    ---
    post:
      tags:
        - api
      description: |
        Executes a scenario by *scenario_id*. If the scenario does not exist, a 404 error is returned.

        !!! Example

            === "Curl"
                ```shell
                    curl -X POST http://localhost:5000/api/v1/scenarios/submit/SCENARIO_658d-5834-4d73-84e4-a6343df5e08c
                ```
                In this example the REST API is served on port 5000 on localhost. We are using curl command line
                client.

                `SCENARIO_63cb358d-5834-4d73-84e4-a6343df5e08c` is the value of the *scenario_id* parameter. It
                represents the identifier of the Scenario we want to submit.

                Here is the output message example:
                ```
                {"message": "Executed scenario SCENARIO_63cb358d-5834-4d73-84e4-a6343df5e08c."}
                ```

            === "Python"
                This Python example requires the 'requests' package to be installed (`pip install requests`).
                ```python
                import requests
                response = requests.post(
                    "http://localhost:5000/api/v1/scenarios/submit/SCENARIO_63cb358d-5834-4d73-84e4-a6343df5e08c"
                )
                print(response)
                print(response.json())
                ```
                `SCENARIO_63cb358d-5834-4d73-84e4-a6343df5e08c` is the value of the *scenario_id* parameter. It
                represents the identifier of the Scenario we want to submit.

                Here is the output example:
                ```
                <Response [202]>
                {"message": "Executed scenario SCENARIO_63cb358d-5834-4d73-84e4-a6343df5e08c."}
                ```

        !!! Note
            When the authorization feature is activated (available in Taipy Enterprise edition only), this endpoint
            requires the `TAIPY_EXECUTOR` role.

      parameters:
        - in: path
          name: scenario_id
          schema:
            type: string
          description: The identifier of the scenario to submit.
      responses:
        202:
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
                    description: Status message.
                  scenario: ScenarioSchema
        404:
          description: No scenario has the *scenario_id* identifier.
    """

    def __init__(self, **kwargs):
        self.logger = kwargs.get("logger")

    @_middleware
    def post(self, scenario_id):
        _get_or_raise(scenario_id)
        manager = _ScenarioManagerFactory._build_manager()
        manager._submit(scenario_id)
        return {"message": f"Scenario {scenario_id} was submitted."}
