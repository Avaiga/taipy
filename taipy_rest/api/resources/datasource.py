from flask import jsonify, make_response, request
from flask_restful import Resource
from taipy.config import Config

# from taipy_rest.commons.pagination import paginate
# from taipy_rest.extensions import db
# # from taipy_rest.models import DataSource
from taipy.data.manager.data_manager import DataManager
from taipy.data.scope import Scope
from taipy.exceptions.repository import ModelNotFound

from taipy_rest.api.schemas import (
    CSVDataSourceConfigSchema,
    DataSourceSchema,
    InMemoryDataSourceConfigSchema,
    PickleDataSourceConfigSchema,
    SQLDataSourceConfigSchema,
)

ds_schema_map = {
    "csv": CSVDataSourceConfigSchema,
    "pickle": PickleDataSourceConfigSchema,
    "in_memory": InMemoryDataSourceConfigSchema,
    "sql": SQLDataSourceConfigSchema,
}


class DataSourceResource(Resource):
    """Single object resource

    ---
    get:
      tags:
        - api
      summary: Get a datasource
      description: Get a single datasource by ID
      parameters:
        - in: path
          name: datasource_id
          schema:
            type: string
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  datasource: DataSourceSchema
        404:
          description: datasource does not exists
    put:
      tags:
        - api
      summary: Update a datasource
      description: Update a single datasource by ID
      parameters:
        - in: path
          name: datasource_id
          schema:
            type: string
      requestBody:
        content:
          application/json:
            schema:
              DataSourceSchema
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    example: datasource updated
                  datasource: DataSourceSchema
        404:
          description: datasource does not exists
    delete:
      tags:
        - api
      summary: Delete a datasource
      description: Delete a single datasource by ID
      parameters:
        - in: path
          name: user_id
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
                    example: datasource deleted
        404:
          description: datasource does not exists
    """

    def get(self, datasource_id):
        try:
            schema = DataSourceSchema()
            manager = DataManager()
            datasource = manager.get(datasource_id)
            return {"datasource": schema.dump(datasource)}
        except ModelNotFound:
            return make_response(
                jsonify({"message": f"DataSource {datasource_id} not found"}), 404
            )

    def delete(self, datasource_id):
        manager = DataManager()
        manager.delete(datasource_id)

        return {"msg": f"datasource {datasource_id} deleted"}


class DataSourceList(Resource):
    """Creation and get_all

    ---
    get:
      tags:
        - api
      summary: Get a list of datasources
      description: Get a list of paginated datasources
      responses:
        200:
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/PaginatedResult'
                  - type: object
                    properties:
                      results:
                        type: array
                        items:
                          $ref: '#/components/schemas/DataSourceSchema'
    post:
      tags:
        - api
      summary: Create a datasource
      description: Create a new datasource
      requestBody:
        content:
          application/json:
            schema:
              DataSourceSchema
      responses:
        201:
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    example: datasource created
                  datasource: DataSourceSchema
    """

    def get(self):
        schema = DataSourceSchema(many=True)
        manager = DataManager()
        datasources = manager.get_all()
        return schema.dump(datasources)

    def post(self):
        req = request.json
        try:
            req["scope"] = Scope[req.get("scope", "").upper()].value
        except KeyError:
            return make_response(jsonify({"message": "Invalid scope"}), 400)
        schema = ds_schema_map.get(req.get("storage_type"))()
        manager = DataManager()
        datasource_config = Config.add_data_source(**schema.load(req))
        manager._create_and_set(datasource_config, None)

        return {
            "msg": "datasource created",
            "datasource": schema.dump(datasource_config),
        }, 201
