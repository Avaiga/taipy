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

from typing import List

import numpy as np
import pandas as pd
from flask import jsonify, make_response, request
from flask_restful import Resource

from taipy.config import Config
from taipy.core.data._data_manager_factory import _DataManagerFactory
from taipy.core.data.operator import Operator
from taipy.core.exceptions.exceptions import NonExistingDataNode

from ...commons.to_from_model import _to_model
from ..middlewares._middleware import _middleware
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

REPOSITORY = "data"


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

    def __init__(self, **kwargs):
        self.logger = kwargs.get("logger")

    @_middleware
    def get(self, datanode_id):
        schema = DataNodeSchema()
        manager = _DataManagerFactory._build_manager()
        datanode = manager._get(datanode_id)
        if not datanode:
            return make_response(jsonify({"message": f"DataNode {datanode_id} not found"}), 404)
        return {"datanode": schema.dump(_to_model(REPOSITORY, datanode, class_map=datanode.storage_type()))}

    @_middleware
    def delete(self, datanode_id):
        try:
            manager = _DataManagerFactory._build_manager()
            manager._delete(datanode_id)
        except NonExistingDataNode:
            return make_response(jsonify({"message": f"DataNode {datanode_id} not found"}), 404)
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
              DataNodeSchema
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
                  datanode: DataNodeSchema
    """

    def __init__(self, **kwargs):
        self.logger = kwargs.get("logger")

    def fetch_config(self, config_id):
        return Config.data_nodes[config_id]

    @_middleware
    def get(self):
        schema = DataNodeSchema(many=True)
        manager = _DataManagerFactory._build_manager()
        datanodes = [
            _to_model(REPOSITORY, datanode, class_map=datanode.storage_type()) for datanode in manager._get_all()
        ]
        return schema.dump(datanodes)

    @_middleware
    def post(self):
        args = request.args
        config_id = args.get("config_id")

        if not config_id:
            return {"msg": "Config id is mandatory"}, 400

        try:
            config = self.fetch_config(config_id)
            schema = ds_schema_map.get(config.storage_type)()
            manager = _DataManagerFactory._build_manager()
            manager._bulk_get_or_create({config})

            return {
                "msg": "datanode created",
                "datanode": schema.dump(config),
            }, 201
        except KeyError:
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

    def __init__(self, **kwargs):
        self.logger = kwargs.get("logger")

    def __make_operators(self, schema: DataNodeFilterSchema) -> List:
        return [
            (
                x.get("key"),
                x.get("value"),
                Operator(getattr(Operator, x.get("operator", "").upper())),
            )
            for x in schema.get("operators")
        ]

    @_middleware
    def get(self, datanode_id):
        try:
            schema = DataNodeFilterSchema()
            manager = _DataManagerFactory._build_manager()
            datanode = manager._get(datanode_id)

            data = request.get_json(silent=True)
            operators = self.__make_operators(schema.load(data)) if data else []
            data = datanode.filter(operators)
            if isinstance(data, pd.DataFrame):
                data = data.to_dict(orient="records")
            elif isinstance(data, np.ndarray):
                data = list(data)
            return {"data": data}
        except NonExistingDataNode:
            return make_response(jsonify({"message": f"DataNode {datanode_id} not found"}), 404)


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

    def __init__(self, **kwargs):
        self.logger = kwargs.get("logger")

    @_middleware
    def put(self, datanode_id):
        try:
            manager = _DataManagerFactory._build_manager()
            data = request.json
            datanode = manager._get(datanode_id)
            datanode.write(data)
            return {"message": "DataNode data successfully updated"}
        except NonExistingDataNode:
            return make_response(jsonify({"message": f"DataNode {datanode_id} not found"}), 404)
