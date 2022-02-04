import importlib
from datetime import datetime

from flask import jsonify, make_response, request
from flask_restful import Resource
from taipy.common.frequency import Frequency

from taipy.cycle.manager import CycleManager
from taipy.exceptions.cycle import NonExistingCycle
from taipy.exceptions.repository import ModelNotFound

from taipy_rest.api.schemas import CycleSchema, CycleResponseSchema
from taipy.cycle.cycle import Cycle

from taipy_rest.config import TAIPY_SETUP_FILE


class CycleResource(Resource):
    """Single object resource

    ---
    get:
      tags:
        - api
      summary: Get a cycle
      description: Get a single cycle by ID
      parameters:
        - in: path
          name: cycle_id
          schema:
            type: string
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  cycle: CycleResponseSchema
        404:
          description: cycle does not exist
    delete:
      tags:
        - api
      summary: Delete a cycle
      description: Delete a single cycle by ID
      parameters:
        - in: path
          name: cycle_id
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
                    example: cycle deleted
        404:
          description: cycle does not exist
    """

    def get(self, cycle_id):
        try:
            schema = CycleResponseSchema()
            manager = CycleManager()
            cycle = manager.get(cycle_id)
            return {"cycle": schema.dump(manager.repository.to_model(cycle))}
        except NonExistingCycle:
            return make_response(
                jsonify({"message": f"Cycle {cycle_id} not found"}), 404
            )

    def delete(self, cycle_id):
        try:
            manager = CycleManager()
            manager.delete(cycle_id)
        except ModelNotFound:
            return make_response(
                jsonify({"message": f"DataNode {cycle_id} not found"}), 404
            )

        return {"msg": f"cycle {cycle_id} deleted"}


class CycleList(Resource):
    """Creation and get_all

    ---
    get:
      tags:
        - api
      summary: Get a list of cycles
      description: Get a list of paginated cycles
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
                          $ref: '#/components/schemas/CycleResponseSchema'
    post:
      tags:
        - api
      summary: Create a cycle
      description: Create a new cycle
      requestBody:
        content:
          application/json:
            schema:
              CycleSchema
      responses:
        201:
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    example: cycle created
                  cycle: CycleSchema
    """

    def __init__(self):
        spec = importlib.util.spec_from_file_location("taipy_setup", TAIPY_SETUP_FILE)
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)

    def fetch_config(self, config_name):
        return getattr(self.module, config_name)

    def get(self):
        schema = CycleSchema(many=True)
        manager = CycleManager()
        cycles = manager.get_all()
        cycles_model = [manager.repository.to_model(t) for t in cycles]
        return schema.dump(cycles_model)

    def post(self):
        schema = CycleSchema()
        manager = CycleManager()

        cycle = self.__create_cycle_from_schema(schema.load(request.json))
        manager.set(cycle)

        return {
            "msg": "cycle created",
            "cycle": schema.dump(manager.repository.to_model(cycle)),
        }, 201

    def __create_cycle_from_schema(self, cycle_schema: CycleSchema):
        return Cycle(
            id=cycle_schema.get("id"),
            frequency=Frequency(
                getattr(Frequency, cycle_schema.get("frequency", "").upper())
            ),
            properties=cycle_schema.get("properties", {}),
            creation_date=datetime.fromisoformat(cycle_schema.get("creation_date")),
            start_date=datetime.fromisoformat(cycle_schema.get("start_date")),
            end_date=datetime.fromisoformat(cycle_schema.get("end_date")),
        )
