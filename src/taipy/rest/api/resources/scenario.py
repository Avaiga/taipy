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

from flask import request
from flask_restful import Resource

from taipy.config.config import Config
from taipy.core.exceptions.exceptions import NonExistingScenario, NonExistingScenarioConfig
from taipy.core.scenario._scenario_manager_factory import _ScenarioManagerFactory

from ...commons.to_from_model import _to_model
from ..exceptions.exceptions import ConfigIdMissingException
from ..middlewares._middleware import _middleware
from ..schemas import ScenarioResponseSchema


def _get_or_raise(scenario_id: str):
    manager = _ScenarioManagerFactory._build_manager()
    scenario = manager._get(scenario_id)
    if scenario is None:
        raise NonExistingScenario(scenario_id)
    return scenario


REPOSITORY = "scenario"


class ScenarioResource(Resource):
    """Single object resource

    ---
    get:
      tags:
        - api
      summary: Get a scenario.
      description: |
        Return a single scenario by *scenario_id*. If the scenario does not exist, a 404 error is returned.

        !!! Note
          When the authorization feature is activated (available in the **Enterprise** edition only), this endpoint requires `TAIPY_READER` role.

        Code example:

        ```
          curl -X GET http://localhost:5000/api/v1/scenarios/SCENARIO_my_config_75750ed8-4e09-4e00-958d-e352ee426cc9
        ```

      parameters:
        - in: path
          name: scenario_id
          schema:
            type: string
          description: The identifier of the scenario.
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
      summary: Delete a scenario.
      description: |
        Delete a scenario. If the scenario does not exist, a 404 error is returned.

        !!! Note
          When the authorization feature is activated (available in the **Enterprise** edition only), this endpoint requires `TAIPY_EDITOR` role.

        Code example:

        ```shell
          curl -X DELETE http://localhost:5000/api/v1/scenarios/SCENARIO_my_config_75750ed8-4e09-4e00-958d-e352ee426cc9
        ```

      parameters:
        - in: path
          name: scenario_id
          schema:
            type: string
          description: The identifier of the scenario.
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
        Return an array of all scenarios.

        !!! Note
          When the authorization feature is activated (available in the **Enterprise** edition only), this endpoint requires `TAIPY_READER` role.

        Code example:

        ```shell
          curl -X GET http://localhost:5000/api/v1/scenarios
        ```

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
      summary: Create a scenario.
      description: |
        Create a new scenario from its *config_id*. If the config does not exist, a 404 error is returned.

        !!! Note
          When the authorization feature is activated (available in the **Enterprise** edition only), this endpoint requires `TAIPY_EDITOR` role.

        Code example:

        ```shell
          curl -X POST http://localhost:5000/api/v1/scenarios?config_id=my_scenario_config
        ```
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
        config = Config.scenarios.get(config_id)
        if not config:
            raise NonExistingScenarioConfig(config_id)
        return config

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
      summary: Execute a scenario.
      description: |
        Execute a scenario by *scenario_id*. If the scenario does not exist, a 404 error is returned.

        !!! Note
          When the authorization feature is activated (available in the **Enterprise** edition only), this endpoint requires `TAIPY_EXECUTOR` role.

        Code example:

        ```shell
          curl -X POST http://localhost:5000/api/v1/scenarios/submit/SCENARIO_my_config_75750ed8-4e09-4e00-958d-e352ee426cc9
        ```

      parameters:
        - in: path
          name: scenario_id
          schema:
            type: string
      responses:
        204:
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
