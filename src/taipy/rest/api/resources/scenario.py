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

from flask import jsonify, make_response, request
from flask_restful import Resource

from taipy.core.config.config import Config
from taipy.core.exceptions.exceptions import ModelNotFound, NonExistingScenario
from taipy.core.pipeline._pipeline_manager_factory import _PipelineManagerFactory
from taipy.core.scenario._scenario_manager_factory import _ScenarioManagerFactory
from taipy.core.scenario.scenario import Scenario

from ...commons.to_from_model import to_model
from ..middlewares._middleware import _middleware
from ..schemas import ScenarioResponseSchema, ScenarioSchema

REPOSITORY = "scenario"


class ScenarioResource(Resource):
    """Single object resource

    ---
    get:
      tags:
        - api
      summary: Get a scenario
      description: Get a single scenario by ID
      parameters:
        - in: path
          name: scenario_id
          schema:
            type: string
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  scenario: ScenarioSchema
        404:
          description: scenario does not exist
    delete:
      tags:
        - api
      summary: Delete a scenario
      description: Delete a single scenario by ID
      parameters:
        - in: path
          name: scenario_id
          schema:
            type: integer
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    example: scenario deleted
        404:
          description: scenario does not exist
    """

    def __init__(self, **kwargs):
        self.logger = kwargs.get("logger")

    @_middleware
    def get(self, scenario_id):
        schema = ScenarioResponseSchema()
        manager = _ScenarioManagerFactory._build_manager()
        scenario = manager._get(scenario_id)
        if not scenario:
            return make_response(jsonify({"message": f"Scenario {scenario_id} not found"}), 404)
        return {"scenario": schema.dump(to_model(REPOSITORY, scenario))}

    @_middleware
    def delete(self, scenario_id):
        try:
            manager = _ScenarioManagerFactory._build_manager()
            manager._delete(scenario_id)
        except ModelNotFound:
            return make_response(jsonify({"message": f"DataNode {scenario_id} not found"}), 404)

        return {"msg": f"scenario {scenario_id} deleted"}


class ScenarioList(Resource):
    """Creation and get_all

    ---
    get:
      tags:
        - api
      summary: Get a list of scenarios
      description: Get a list of paginated scenarios
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
      summary: Create a scenario
      description: Create a new scenario
      requestBody:
        content:
          application/json:
            schema:
              ScenarioSchema
      responses:
        201:
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    example: scenario created
                  scenario: ScenarioSchema
    """

    def __init__(self, **kwargs):
        self.logger = kwargs.get("logger")

    def fetch_config(self, config_id):
        return Config.scenarios[config_id]

    @_middleware
    def get(self):
        schema = ScenarioResponseSchema(many=True)
        manager = _ScenarioManagerFactory._build_manager()
        scenarios = [to_model(REPOSITORY, scenario) for scenario in manager._get_all()]
        return schema.dump(scenarios)

    @_middleware
    def post(self):
        args = request.args
        config_id = args.get("config_id")

        response_schema = ScenarioResponseSchema()
        manager = _ScenarioManagerFactory._build_manager()

        if not config_id:
            return {"msg": "Config id is mandatory"}, 400

        try:
            config = self.fetch_config(config_id)
            scenario = manager._create(config)

            return {
                "msg": "scenario created",
                "scenario": response_schema.dump(to_model(REPOSITORY, scenario)),
            }, 201
        except KeyError:
            return {"msg": f"Config id {config_id} not found"}, 404

    def __create_scenario_from_schema(self, scenario_schema: ScenarioSchema):
        pipeline_manager = _PipelineManagerFactory._build_manager()
        return Scenario(
            config_id=scenario_schema.get("name"),
            properties=scenario_schema.get("properties", {}),
            pipelines=[pipeline_manager._get(pl) for pl in scenario_schema.get("pipeline_ids")],
            scenario_id=scenario_schema.get("id"),
            is_master=scenario_schema.get("master_scenario"),
            cycle=scenario_schema.get("cycle"),
        )


class ScenarioExecutor(Resource):
    """Execute a scenario

    ---
    post:
      tags:
        - api
      summary: Execute a scenario
      description: Execute a scenario
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
                  msg:
                    type: string
                    example: scenario created
                  scenario: ScenarioSchema
      404:
          description: scenario does not exist
    """

    def __init__(self, **kwargs):
        self.logger = kwargs.get("logger")

    @_middleware
    def post(self, scenario_id):
        try:
            manager = _ScenarioManagerFactory._build_manager()
            manager._submit(scenario_id)
            return {"message": f"Executed scenario {scenario_id}"}
        except NonExistingScenario:
            return make_response(jsonify({"message": f"Scenario {scenario_id} not found"}), 404)
