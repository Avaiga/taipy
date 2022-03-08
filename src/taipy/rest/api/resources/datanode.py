import importlib
import os
from typing import List

import numpy as np
import pandas as pd
from flask import jsonify, make_response, request
from flask_restful import Resource
from taipy.core.data._data_manager import _DataManager as DataManager
from taipy.core.data.operator import Operator
from taipy.core.exceptions.data_node import NonExistingDataNode

from ...config import TAIPY_SETUP_FILE
from ..schemas import (
    CSVDataNodeConfigSchema,
    DataNodeFilterSchema,
    DataNodeSchema,
    InMemoryDataNodeConfigSchema,
    PickleDataNodeConfigSchema,
    SQLDataNodeConfigSchema,
)

ds_schema_map = {
    "csv": CSVDataNodeConfigSchema,
    "pickle": PickleDataNodeConfigSchema,
    "in_memory": InMemoryDataNodeConfigSchema,
    "sql": SQLDataNodeConfigSchema,
}


class DataNodeResource(Resource):
    """Single object resource

    ---
    get:
      tags:
        - api
      summary: Get a datanode
      description: Get a single datanode by ID
      parameters:
        - in: path
          name: datanode_id
          schema:
            type: string
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  datanode: DataNodeSchema
        404:
          description: datanode does not exist
    delete:
      tags:
        - api
      summary: Delete a datanode
      description: Delete a single datanode by ID
      parameters:
        - in: path
          name: datanode_id
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
                    example: datanode deleted
        404:
          description: datanode does not exist
    """

    def __init__(self):
        if os.path.exists(TAIPY_SETUP_FILE):
            spec = importlib.util.spec_from_file_location(
                "taipy_setup", TAIPY_SETUP_FILE
            )
            self.module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(self.module)

    def get(self, datanode_id):
        schema = DataNodeSchema()
        manager = DataManager()
        datanode = manager._get(datanode_id)
        if not datanode:
            return make_response(
                jsonify({"message": f"DataNode {datanode_id} not found"}), 404
            )
        return {"datanode": schema.dump(datanode)}

    def delete(self, datanode_id):
        try:
            manager = DataManager()
            manager._delete(datanode_id)
        except NonExistingDataNode:
            return make_response(
                jsonify({"message": f"DataNode {datanode_id} not found"}), 404
            )
        return {"msg": f"datanode {datanode_id} deleted"}


class DataNodeList(Resource):
    """Creation and get_all

    ---
    get:
      tags:
        - api
      summary: Get a list of datanodes
      description: Get a list of paginated datanodes
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
                          $ref: '#/components/schemas/DataNodeSchema'
    post:
      tags:
        - api
      summary: Create a datanode
      description: Create a new datanode
      requestBody:
        content:
          application/json:
            schema:
              DataNodeConfigSchema
      responses:
        201:
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    example: datanode created
                  datanode: DataNodeConfigSchema
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
        schema = DataNodeSchema(many=True)
        manager = DataManager()
        datanodes = manager._get_all()
        return schema.dump(datanodes)

    def post(self):
        args = request.args
        config_id = args.get("config_id")

        if not config_id:
            return {"msg": "Config id is mandatory"}, 400

        try:
            config = self.fetch_config(config_id)
            schema = ds_schema_map.get(config.storage_type)()
            manager = DataManager()
            manager._get_or_create(config)

            return {
                "msg": "datanode created",
                "datanode": schema.dump(config),
            }, 201
        except AttributeError:
            return {"msg": f"Config id {config_id} not found"}, 404


class DataNodeReader(Resource):
    """Single object resource

    ---
    get:
      tags:
        - api
      summary: Read a DataNode content
      description: Return a content of a DataNode
      parameters:
        - in: path
          name: datanode_id
          schema:
            type: string
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  datanode: DataNodeSchema
        404:
          description: datanode does not exist
    """

    def __init__(self):
        if os.path.exists(TAIPY_SETUP_FILE):
            spec = importlib.util.spec_from_file_location(
                "taipy_setup", TAIPY_SETUP_FILE
            )
            self.module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(self.module)

    def __make_operators(self, schema: DataNodeFilterSchema) -> List:
        return [
            (
                x.get("key"),
                x.get("value"),
                Operator(getattr(Operator, x.get("operator", "").upper())),
            )
            for x in schema.get("operators")
        ]

    def get(self, datanode_id):
        try:
            schema = DataNodeFilterSchema()
            manager = DataManager()
            datanode = manager._get(datanode_id)

            data = request.json
            operators = self.__make_operators(schema.load(data)) if data else []
            data = datanode.filter(operators)
            if isinstance(data, pd.DataFrame):
                data = data.to_dict(orient="records")
            elif isinstance(data, np.ndarray):
                data = list(data)
            return {"data": data}
        except NonExistingDataNode:
            return make_response(
                jsonify({"message": f"DataNode {datanode_id} not found"}), 404
            )


class DataNodeWriter(Resource):
    """Single object resource

    ---
    put:
      tags:
        - api
      summary: Write new data to DataNode
      description: Write new data to DataNode
      parameters:
        - in: path
          name: datanode_id
          schema:
            type: string
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  datanode: DataNodeSchema
        404:
          description: datanode does not exist
    """

    def put(self, datanode_id):
        try:
            manager = DataManager()
            data = request.json
            datanode = manager._get(datanode_id)
            datanode.write(data)
            return {"message": "DataNode data successfully updated"}
        except NonExistingDataNode:
            return make_response(
                jsonify({"message": f"DataNode {datanode_id} not found"}), 404
            )
