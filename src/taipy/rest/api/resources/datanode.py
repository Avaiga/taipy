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

from taipy.config.config import Config
from taipy.core.data._data_manager_factory import _DataManagerFactory
from taipy.core.data.operator import Operator
from taipy.core.exceptions.exceptions import NonExistingDataNode

from ...commons.to_from_model import _to_model
from ..middlewares._middleware import _middleware
from ..schemas import (
    CSVDataNodeConfigSchema,
    DataNodeFilterSchema,
    DataNodeSchema,
    ExcelDataNodeConfigSchema,
    GenericDataNodeConfigSchema,
    InMemoryDataNodeConfigSchema,
    JSONDataNodeConfigSchema,
    PickleDataNodeConfigSchema,
    SQLDataNodeConfigSchema,
)

ds_schema_map = {
    "csv": CSVDataNodeConfigSchema,
    "pickle": PickleDataNodeConfigSchema,
    "in_memory": InMemoryDataNodeConfigSchema,
    "sql": SQLDataNodeConfigSchema,
    "excel": ExcelDataNodeConfigSchema,
    "generic": GenericDataNodeConfigSchema,
    "json": JSONDataNodeConfigSchema,
}

REPOSITORY = "data"


class DataNodeResource(Resource):
    """Single object resource

    ---
    get:
      tags:
        - api
      summary: Get a data node.
      description: |
        Return a single data node by *datanode_id*. If the data node does not exist, a 404 error is returned.

        !!! Note
          When the authorization feature is activated (available in the **Enterprise** edition only), this endpoint requires `TAIPY_READER` role.

        Code example:

        ```shell
          curl -X GET http://localhost:5000/api/v1/datanodes/DATANODE_my_config_75750ed8-4e09-4e00-958d-e352ee426cc9
        ```
      parameters:
        - in: path
          name: datanode_id
          schema:
            type: string
          description: The identifier of the data node.
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  datanode: DataNodeSchema
        404:
          description: No data node has the *datanode_id* identifier.
    delete:
      tags:
        - api
      summary: Delete a data node.
      description: |
        Delete a data node. If the data node does not exist, a 404 error is returned.

        !!! Note
          When the authorization feature is activated (available in the **Enterprise** edition only), this endpoint requires `TAIPY_EDITOR` role.

        Code example:

        ```shell
          curl -X DELETE http://localhost:5000/api/v1/datanodes/DATANODE_my_config_75750ed8-4e09-4e00-958d-e352ee426cc9
        ```

      parameters:
        - in: path
          name: datanode_id
          schema:
            type: string
          description: The identifier of the data node.
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    description: Status message.
        404:
          description: No data node has the *datanode_id* identifier.
    """

    def __init__(self, **kwargs):
        self.logger = kwargs.get("logger")

    @_middleware
    def get(self, datanode_id):
        schema = DataNodeSchema()
        manager = _DataManagerFactory._build_manager()
        datanode = manager._get(datanode_id)
        if not datanode:
            return make_response(jsonify({"message": f"Data node {datanode_id} not found"}), 404)
        return {"datanode": schema.dump(_to_model(REPOSITORY, datanode, class_map=datanode.storage_type()))}

    @_middleware
    def delete(self, datanode_id):
        try:
            manager = _DataManagerFactory._build_manager()
            manager._delete(datanode_id)
        except NonExistingDataNode:
            return make_response(jsonify({"message": f"Data node {datanode_id} not found"}), 404)
        return {"msg": f"Data node {datanode_id} deleted."}


class DataNodeList(Resource):
    """Creation and get_all

    ---
    get:
      tags:
        - api
      summary: Get all data nodes.
      description: |
        Returns an array of all data nodes.

        !!! Note
          When the authorization feature is activated (available in the **Enterprise** edition only), this endpoint requires `TAIPY_READER` role.

        Code example:

        ```shell
          curl -X GET http://localhost:5000/api/v1/datanodes
        ```
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
      summary: Create a data node.
      description: |
        Create a data node from its *config_id*. If the config does not exist, a 404 error is returned.

        !!! Note
          When the authorization feature is activated (available in the **Enterprise** edition only), this endpoint requires `TAIPY_EDITOR` role.

        Code example:

        ```shell
          curl -X POST http://localhost:5000/api/v1/datanodes?config_id=my_data_node_config
        ```
      parameters:
        - in: query
          name: config_id
          schema:
            type: string
          description: The identifier of the data node configuration.
      responses:
        201:
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    description: Status message.
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
                "msg": "Data node created.",
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
      summary: Read a data node.
      description: |
        Return the data read from a data node by *datanode_id*. If the data node does not exist, a 404 error is returned.

        !!! Note
          When the authorization feature is activated (available in the **Enterprise** edition only), this endpoint requires `TAIPY_READER` role.

        Code example:

        ```shell
          curl -X GET http://localhost:5000/api/v1/datanodes/DATANODE_my_config_75750ed8-4e09-4e00-958d-e352ee426cc9/read
        ```

        Code example with filters:

        ```shell
          curl -X GET -H 'Content-Type: application/json' -d '{"operators": [{"key": "foo", "value": 10, "operator": ">"}], "join_operator": "AND"}' http://localhost:5000/api/v1/datanodes/DATANODE_my_config_75750ed8-4e09-4e00-958d-e352ee426cc9/read
        ```

      parameters:
        - in: path
          name: datanode_id
          schema:
            type: string
      requestBody:
        content:
          application/json:
            schema:
              DataNodeFilterSchema
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  datanode: DataNodeSchema
        404:
          description: No data node has the *datanode_id* identifier.
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
        schema = DataNodeFilterSchema()
        manager = _DataManagerFactory._build_manager()
        data_node = manager._get(datanode_id)
        data = request.get_json(silent=True)
        if not data_node:
            return make_response(jsonify({"message": f"Data node {datanode_id} not found"}), 404)
        operators = self.__make_operators(schema.load(data)) if data else []
        data = data_node.filter(operators)
        if isinstance(data, pd.DataFrame):
            data = data.to_dict(orient="records")
        elif isinstance(data, np.ndarray):
            data = list(data)
        return {"data": data}


class DataNodeWriter(Resource):
    """Single object resource

    ---
    put:
      tags:
        - api
      summary: Write into a data node.
      description: |
        Write data from request body into a data node by *datanode_id*. If the data node does not exist, a 404 error is returned.

        !!! Note
          When the authorization feature is activated (available in the **Enterprise** edition only), this endpoint requires `TAIPY_EDITOR` role.

        Code example:

        ```shell
          curl -X PUT -d '[{"path": "/abc", "type": 1}, {"path": "/def", "type": 2}]' -H 'Content-Type: application/json'  http://localhost:5000/api/v1/datanodes/DATANODE_my_config_75750ed8-4e09-4e00-958d-e352ee426cc9/write
        ```

      parameters:
        - in: path
          name: datanode_id
          schema:
            type: string
      requestBody:
        content:
          application/json:
            schema:
              Any
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  datanode: DataNodeSchema
        404:
          description: No data node has the *datanode_id* identifier.
    """

    def __init__(self, **kwargs):
        self.logger = kwargs.get("logger")

    @_middleware
    def put(self, datanode_id):
        manager = _DataManagerFactory._build_manager()
        data = request.json
        data_node = manager._get(datanode_id)
        if not data_node:
            return make_response(jsonify({"message": f"Data node {datanode_id} not found"}), 404)
        data_node.write(data)
        return {"message": "Data node is successfully written"}
