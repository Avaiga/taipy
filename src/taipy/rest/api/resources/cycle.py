from datetime import datetime

from flask import jsonify, make_response, request
from flask_restful import Resource
from taipy.core import Cycle, Frequency
from taipy.core.config.config import Config
from taipy.core.cycle._cycle_manager import _CycleManager as CycleManager
from taipy.core.exceptions.exceptions import ModelNotFound

from ...commons.to_from_model import to_model
from ..schemas import CycleResponseSchema, CycleSchema

REPOSITORY = "cycle"


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
                  cycle: CycleSchema
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

    def __init__(self, **kwargs):
        self.logger = kwargs.get("logger")

    def get(self, cycle_id):
        schema = CycleResponseSchema()
        manager = CycleManager()
        cycle = manager._get(cycle_id)
        if not cycle:
            return make_response(jsonify({"message": f"Cycle {cycle_id} not found"}), 404)
        return {"cycle": schema.dump(to_model(REPOSITORY, cycle))}

    def delete(self, cycle_id):
        try:
            manager = CycleManager()
            manager._delete(cycle_id)
        except ModelNotFound:
            return make_response(jsonify({"message": f"DataNode {cycle_id} not found"}), 404)

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
                          $ref: '#/components/schemas/CycleSchema'
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

    def __init__(self, **kwargs):
        self.logger = kwargs.get("logger")

    def fetch_config(self, config_id):
        return Config.cycles[config_id]

    def get(self):
        schema = CycleResponseSchema(many=True)
        manager = CycleManager()
        cycles = [to_model(REPOSITORY, cycle) for cycle in manager._get_all()]
        return schema.dump(cycles)

    def post(self):
        schema = CycleResponseSchema()
        manager = CycleManager()

        cycle = self.__create_cycle_from_schema(schema.load(request.json))
        manager._set(cycle)

        return {
            "msg": "cycle created",
            "cycle": schema.dump(to_model(REPOSITORY, cycle)),
        }, 201

    def __create_cycle_from_schema(self, cycle_schema: CycleSchema):
        return Cycle(
            id=cycle_schema.get("id"),
            frequency=Frequency(getattr(Frequency, cycle_schema.get("frequency", "").upper())),
            properties=cycle_schema.get("properties", {}),
            creation_date=datetime.fromisoformat(cycle_schema.get("creation_date")),
            start_date=datetime.fromisoformat(cycle_schema.get("start_date")),
            end_date=datetime.fromisoformat(cycle_schema.get("end_date")),
        )
