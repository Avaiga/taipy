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

from datetime import datetime

from flask import jsonify, make_response, request
from flask_restful import Resource

from taipy.config.scenario.frequency import Frequency
from taipy.core import Cycle
from taipy.core.cycle._cycle_manager_factory import _CycleManagerFactory
from taipy.core.exceptions.exceptions import ModelNotFound

from ...commons.to_from_model import _to_model
from ..middlewares._middleware import _middleware
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

    @_middleware
    def get(self, cycle_id):
        schema = CycleResponseSchema()
        manager = _CycleManagerFactory._build_manager()
        cycle = manager._get(cycle_id)
        if not cycle:
            return make_response(jsonify({"message": f"Cycle {cycle_id} not found"}), 404)
        return {"cycle": schema.dump(_to_model(REPOSITORY, cycle))}

    @_middleware
    def delete(self, cycle_id):
        try:
            manager = _CycleManagerFactory._build_manager()
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

    @_middleware
    def get(self):
        schema = CycleResponseSchema(many=True)
        manager = _CycleManagerFactory._build_manager()
        cycles = [_to_model(REPOSITORY, cycle) for cycle in manager._get_all()]
        return schema.dump(cycles)

    @_middleware
    def post(self):
        schema = CycleResponseSchema()
        manager = _CycleManagerFactory._build_manager()

        cycle = self.__create_cycle_from_schema(schema.load(request.json))
        manager._set(cycle)

        return {
            "msg": "cycle created",
            "cycle": schema.dump(_to_model(REPOSITORY, cycle)),
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
