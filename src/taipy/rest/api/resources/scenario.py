import importlib
import os

from flask import jsonify, make_response, request
from flask_restful import Resource
from taipy.core.exceptions.repository import ModelNotFound
from taipy.core.exceptions.scenario import NonExistingScenario
from taipy.core.pipeline._pipeline_manager import _PipelineManager as PipelineManager
from taipy.core.scenario.scenario import Scenario
from taipy.core.scenario._scenario_manager import _ScenarioManager as ScenarioManager

from ...config import TAIPY_SETUP_FILE
from ..schemas import ScenarioResponseSchema, ScenarioSchema


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

    def get(self, scenario_id):
        schema = ScenarioResponseSchema()
        manager = ScenarioManager()
        scenario = manager._get(scenario_id)
        if not scenario:
            return make_response(
                jsonify({"message": f"Scenario {scenario_id} not found"}), 404
            )
        return {"scenario": schema.dump(scenario)}

    def delete(self, scenario_id):
        try:
            manager = ScenarioManager()
            manager._delete(scenario_id)
        except ModelNotFound:
            return make_response(
                jsonify({"message": f"DataNode {scenario_id} not found"}), 404
            )

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

    def __init__(self):
        if os.path.exists(TAIPY_SETUP_FILE):
            spec = importlib.util.spec_from_file_location(
                "taipy_setup", TAIPY_SETUP_FILE
            )
            self.module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(self.module)

    def fetch_config(self, config_id):
        return getattr(self.module, config_id)

    def get(self):
        schema = ScenarioResponseSchema(many=True)
        manager = ScenarioManager()
        scenarios = manager._get_all()
        return schema.dump(scenarios)

    def post(self):
        args = request.args
        config_id = args.get("config_id")

        response_schema = ScenarioResponseSchema()
        manager = ScenarioManager()

        if not config_id:
            return {"msg": "Config id is mandatory"}, 400

        try:
            config = self.fetch_config(config_id)
            scenario = manager._create(config)

            return {
                "msg": "scenario created",
                "scenario": response_schema.dump(scenario),
            }, 201
        except AttributeError:
            return {"msg": f"Config id {config_id} not found"}, 404

    def __create_scenario_from_schema(self, scenario_schema: ScenarioSchema):
        pipeline_manager = PipelineManager()
        return Scenario(
            config_id=scenario_schema.get("name"),
            properties=scenario_schema.get("properties", {}),
            pipelines=[
                pipeline_manager._get(pl) for pl in scenario_schema.get("pipeline_ids")
            ],
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

    def post(self, scenario_id):
        try:
            manager = ScenarioManager()
            manager._submit(scenario_id)
            return {"message": f"Executed scenario {scenario_id}"}
        except NonExistingScenario:
            return make_response(
                jsonify({"message": f"Scenario {scenario_id} not found"}), 404
            )
