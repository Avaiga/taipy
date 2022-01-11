from flask import jsonify, make_response, request
from flask_restful import Resource
from taipy.pipeline import PipelineManager

from taipy.scenario.manager import ScenarioManager
from taipy.exceptions.scenario import NonExistingScenario
from taipy.exceptions.repository import ModelNotFound

from taipy_rest.api.schemas import ScenarioSchema, ScenarioResponseSchema
from taipy.scenario.scenario import Scenario


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
        try:
            schema = ScenarioResponseSchema()
            manager = ScenarioManager()
            scenario = manager.get(scenario_id)
            return {"scenario": schema.dump(manager.repository.to_model(scenario))}
        except NonExistingScenario:
            return make_response(
                jsonify({"message": f"Scenario {scenario_id} not found"}), 404
            )

    def delete(self, scenario_id):
        try:
            manager = ScenarioManager()
            manager.delete(scenario_id)
        except ModelNotFound:
            return make_response(
                jsonify({"message": f"DataSource {scenario_id} not found"}), 404
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

    def get(self):
        schema = ScenarioResponseSchema(many=True)
        manager = ScenarioManager()
        scenarios = manager.get_all()
        scenarios_model = [manager.repository.to_model(t) for t in scenarios]
        return schema.dump(scenarios_model)

    def post(self):
        schema = ScenarioSchema()
        response_schema = ScenarioResponseSchema()
        manager = ScenarioManager()
        scenario = self.__create_scenario_from_schema(schema.load(request.json))
        manager.set(scenario)

        return {
            "msg": "scenario created",
            "scenario": response_schema.dump(manager.repository.to_model(scenario)),
        }, 201

    def __create_scenario_from_schema(self, scenario_schema: ScenarioSchema):
        pipeline_manager = PipelineManager()
        return Scenario(
            config_name=scenario_schema.get("name"),
            properties=scenario_schema.get("properties", {}),
            pipelines=[
                pipeline_manager.get(pl) for pl in scenario_schema.get("pipeline_ids")
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
            manager.submit(scenario_id)
            return {"message": f"Executed scenario {scenario_id}"}
        except NonExistingScenario:
            return make_response(
                jsonify({"message": f"Scenario {scenario_id} not found"}), 404
            )
