import importlib

from flask import jsonify, make_response, request
from flask_restful import Resource
from taipy.config import Config

from taipy.data.manager.data_manager import DataManager
from taipy.data.scope import Scope
from taipy.exceptions.data_source import NonExistingDataSource

from taipy_rest.api.schemas import (
    CSVDataSourceConfigSchema,
    DataSourceSchema,
    InMemoryDataSourceConfigSchema,
    PickleDataSourceConfigSchema,
    SQLDataSourceConfigSchema,
    DataSourceConfigSchema,
)
from taipy_rest.config import TAIPY_SETUP_FILE

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
          description: datasource does not exist
    delete:
      tags:
        - api
      summary: Delete a datasource
      description: Delete a single datasource by ID
      parameters:
        - in: path
          name: datasource_id
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
          description: datasource does not exist
    """

    def get(self, datasource_id):
        try:
            schema = DataSourceSchema()
            manager = DataManager()
            datasource = manager.get(datasource_id)
            return {"datasource": schema.dump(datasource)}
        except NonExistingDataSource:
            return make_response(jsonify({"message": f"DataSource {datasource_id} not found"}), 404)

    def delete(self, datasource_id):
        try:
            manager = DataManager()
            manager.delete(datasource_id)
        except NonExistingDataSource:
            return make_response(jsonify({"message": f"DataSource {datasource_id} not found"}), 404)
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
              DataSourceConfigSchema
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
                  datasource: DataSourceConfigSchema
    """

    def __init__(self):
        spec = importlib.util.spec_from_file_location("taipy_setup", TAIPY_SETUP_FILE)
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)

    def fetch_config(self, config_name):
        return getattr(self.module, config_name)

    def get(self):
        schema = DataSourceSchema(many=True)
        manager = DataManager()
        datasources = manager.get_all()
        return schema.dump(datasources)

    def post(self):
        args = request.args
        config_name = args.get("config_name")

        if not config_name:
            return {"msg": "Config name is mandatory"}, 400

        try:
            config = self.fetch_config(config_name)
            schema = ds_schema_map.get(config.storage_type)()
            manager = DataManager()
            manager.get_or_create(config)

            return {
                "msg": "datasource created",
                "datasource": schema.dump(config),
            }, 201
        except AttributeError:
            return {"msg": f"Config name {config_name} not found"}, 404
