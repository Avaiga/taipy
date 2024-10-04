# Copyright 2021-2024 Avaiga Private Limited
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
from flask import request
from flask_restful import Resource

from taipy.common.config import Config
from taipy.core import DataNode
from taipy.core.data._data_manager_factory import _DataManagerFactory
from taipy.core.data.operator import Operator
from taipy.core.exceptions.exceptions import NonExistingDataNode, NonExistingDataNodeConfig

from ...commons.to_from_model import _to_model
from ..exceptions.exceptions import ConfigIdMissingException
from ..middlewares._middleware import _middleware
from ..schemas import (
    CSVDataNodeConfigSchema,
    DataNodeFilterSchema,
    DataNodeSchema,
    ExcelDataNodeConfigSchema,
    GenericDataNodeConfigSchema,
    InMemoryDataNodeConfigSchema,
    JSONDataNodeConfigSchema,
    MongoCollectionDataNodeConfigSchema,
    PickleDataNodeConfigSchema,
    SQLDataNodeConfigSchema,
    SQLTableDataNodeConfigSchema,
)

ds_schema_map = {
    "csv": CSVDataNodeConfigSchema,
    "pickle": PickleDataNodeConfigSchema,
    "in_memory": InMemoryDataNodeConfigSchema,
    "sql_table": SQLTableDataNodeConfigSchema,
    "sql": SQLDataNodeConfigSchema,
    "mongo_collection": MongoCollectionDataNodeConfigSchema,
    "excel": ExcelDataNodeConfigSchema,
    "generic": GenericDataNodeConfigSchema,
    "json": JSONDataNodeConfigSchema,
}

REPOSITORY = "data"


def _get_or_raise(data_node_id: str) -> DataNode:
    if data_node := _DataManagerFactory._build_manager()._get(data_node_id):
        return data_node

    raise NonExistingDataNode(data_node_id)


class DataNodeResource(Resource):
    """Single object resource

    ---
    get:
      tags:
        - api
      description: |
        Returns a `DataNodeSchema^` representing the unique `DataNode^` identified by the *datanode_id*
        given as parameter. If no data node corresponds to *datanode_id*, a `404` error is returned.

        !!! Example

            === "Curl"
                ```shell
                    curl -X GET http://localhost:5000/api/v1/datanodes/DATANODE_hist_cfg_75750ed8-4e09-4e00-958d
                    -e352ee426cc9
                ```
                In this example the REST API is served on port 5000 on localhost. We are using curl command line
                client.

                `DATANODE_hist_cfg_75750ed8-4e09-4e00-958d-e352ee426cc9` is the value of the *datanode_id* parameter. It
                represents the identifier of the data node we want to retrieve.

                In case of success here is an example of the response:
                ``` JSON
                {"datanode": {
                    "id": "DATANODE_historical_data_set_9db1b542-2e45-44e7-8a85-03ef9ead173d",
                    "config_id": "historical_data_set",
                    "scope": "<Scope.SCENARIO: 2>",
                    "storage_type": "csv",
                    "name": "Name of my historical data node",
                    "owner_id": "SCENARIO_my_awesome_scenario_97f3fd67-8556-4c62-9b3b-ef189a599a38",
                    "last_edit_date": "2022-08-10T16:03:40.855082",
                    "job_ids": [],
                    "version": "latest",
                    "validity_days": null,
                    "validity_seconds": null,
                    "edit_in_progress": false,
                    "data_node_properties": {
                        "path": "daily-min-temperatures.csv",
                        "has_header": true}
                    }}
                ```

                In case of failure here is an example of the response:
                ``` JSON
                {"message":"DataNode DATANODE_historical_data_set_9db1b542-2e45-44e7-8a85-03ef9ead173d not found"}
                ```

            === "Python"
                This Python example requires the 'requests' package to be installed (`pip install requests`).
                ```python
                import requests
                response = requests.get(
                    "http://localhost:5000/api/v1/datanodes/DATANODE_historical_data_set_9db1b542-2e45-44e7-8a85-03ef9ead173d"
                )
                print(response)
                print(response.json())
                ```
                `DATANODE_hist_cfg_75750ed8-4e09-4e00-958d-e352ee426cc9` is the value of the *datanode_id* parameter. It
                represents the identifier of the data node we want to retrieve.

                In case of success here is an output example:
                ```
                <Response [200]>
                {"datanode": {
                    "id": "DATANODE_historical_data_set_9db1b542-2e45-44e7-8a85-03ef9ead173d",
                    "config_id": "historical_data_set",
                    "scope": "<Scope.SCENARIO: 2>",
                    "storage_type": "csv",
                    "name": "Name of my historical data node",
                    "owner_id": "SCENARIO_my_awesome_scenario_97f3fd67-8556-4c62-9b3b-ef189a599a38",
                    "last_edit_date": "2022-08-10T16:03:40.855082",
                    "job_ids": [],
                    "version": "latest",
                    "validity_days": null,
                    "validity_seconds": null,
                    "edit_in_progress": false,
                    "data_node_properties": {
                        "path": "daily-min-temperatures.csv",
                        "has_header": true}
                    }}
                ```

                In case of failure here is an output example:
                ```
                <Response [404]>
                {"message":"DataNode DATANODE_historical_data_set_9db1b542-2e45-44e7-8a85-03ef9ead173d not found"}

                ```

        !!! Note
          When the authorization feature is activated (available in Taipy Enterprise edition only), this endpoint
            requires the `TAIPY_READER` role.

      parameters:
        - in: path
          name: datanode_id
          schema:
            type: string
          description: The identifier of the data node to retrieve.

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
        Deletes the `DataNode^` identified by the  *datanode_id* given as parameter. If the data node does not exist,
        a 404 error is returned.

        !!! Example

            === "Curl"
                ```shell
                    curl -X DELETE \
                    http://localhost:5000/api/v1/datanodes/DATANODE_historical_data_set_9db1b542-2e45-44e7-8a85-03ef9ead173d
                ```
                In this example the REST API is served on port 5000 on localhost. We are using curl command line
                client.

                `DATANODE_historical_data_set_9db1b542-2e45-44e7-8a85-03ef9ead173d` is the value of the
                *datanode_id* parameter. It represents the identifier of the data node we want to delete.

                In case of success here is an example of the response:
                ``` JSON
                {"msg": "datanode DATANODE_historical_data_set_9db1b542-2e45-44e7-8a85-03ef9ead173d deleted"}
                ```

                In case of failure here is an example of the response:
                ``` JSON
                {"message": "Data node DATANODE_historical_data_set_9db1b542-2e45-44e7-8a85-03ef9ead173d not found."}
                ```

            === "Python"
                This Python example requires the 'requests' package to be installed (`pip install requests`).
                ```python
                import requests
                response = requests.delete(
                    "http://localhost:5000/api/v1/datanodes/DATANODE_historical_data_set_9db1b542-2e45-44e7-8a85-03ef9ead173d"
                )
                print(response)
                print(response.json())
                ```
                `DATANODE_historical_data_set_9db1b542-2e45-44e7-8a85-03ef9ead173d` is the value of the
                *datanode_id* parameter. It represents the identifier of the Cycle we want to delete.

                In case of success here is an output example:
                ```
                <Response [200]>
                {"msg": "Data node DATANODE_historical_data_set_9db1b542-2e45-44e7-8a85-03ef9ead173d deleted."}
                ```

                In case of failure here is an output example:
                ```
                <Response [404]>
                {'message': 'Data node DATANODE_historical_data_set_9db1b542-2e45-44e7-8a85-03ef9ead173d not found.'}

                ```

        !!! Note
            When the authorization feature is activated (available in Taipy Enterprise edition only), this endpoint
            requires the `TAIPY_EDITOR` role.

      parameters:
        - in: path
          name: datanode_id
          schema:
            type: string
          description: The identifier of the data node to delete.
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
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
        datanode = _get_or_raise(datanode_id)
        return {"datanode": schema.dump(_to_model(REPOSITORY, datanode))}

    @_middleware
    def delete(self, datanode_id):
        _get_or_raise(datanode_id)
        manager = _DataManagerFactory._build_manager()
        manager._delete(datanode_id)
        return {"message": f"Data node {datanode_id} was deleted."}


class DataNodeList(Resource):
    """Creation and get_all

    ---
    get:
      tags:
        - api
      description: |
        Returns a `DataNodeSchema^` list representing all existing data nodes.

        !!! Example

            === "Curl"
                ```shell
                    curl -X GET http://localhost:5000/api/v1/datanodes
                ```
                In this example the REST API is served on port 5000 on localhost. We are using curl command line
                client.

                Here is an example of the response:
                ``` JSON
                [
                    {"datanode": {
                        "id": "DATANODE_historical_data_set_9db1b542-2e45-44e7-8a85-03ef9ead173d",
                        "config_id": "historical_data_set",
                        "scope": "<Scope.SCENARIO: 2>",
                        "storage_type": "csv",
                        "name": "Name of my historical data node",
                        "owner_id": "SCENARIO_my_awesome_scenario_97f3fd67-8556-4c62-9b3b-ef189a599a38",
                        "last_edit_date": "2022-08-10T16:03:40.855082",
                        "job_ids": [],
                        "version": "latest",
                        "validity_days": null,
                        "validity_seconds": null,
                        "edit_in_progress": false,
                        "data_node_properties": {
                            "path": "daily-min-temperatures.csv",
                            "has_header": true}
                    }}
                ]
                ```

                If there is no data node, the response is an empty list as follows:
                ``` JSON
                []
                ```

            === "Python"
                This Python example requires the 'requests' package to be installed (`pip install requests`).
                ```python
                import requests
                response = requests.get("http://localhost:5000/api/v1/datanodes")
                print(response)
                print(response.json())
                ```

                In case of success here is an output example:
                ```
                <Response [200]>
                [
                    {"datanode": {
                        "id": "DATANODE_historical_data_set_9db1b542-2e45-44e7-8a85-03ef9ead173d",
                        "config_id": "historical_data_set",
                        "scope": "<Scope.SCENARIO: 2>",
                        "storage_type": "csv",
                        "name": "Name of my historical data node",
                        "owner_id": "SCENARIO_my_awesome_scenario_97f3fd67-8556-4c62-9b3b-ef189a599a38",
                        "last_edit_date": "2022-08-10T16:03:40.855082",
                        "job_ids": [],
                        "version": "latest",
                        "validity_days": null,
                        "validity_seconds": null,
                        "edit_in_progress": false,
                        "data_node_properties": {
                            "path": "daily-min-temperatures.csv",
                            "has_header": true}
                    }}
                ]
                ```

                If there is no data node, the response is an empty list as follows:
                ```
                <Response [200]>
                []
                ```

        !!! Note
            When the authorization feature is activated (available in Taipy Enterprise edition only), this endpoint
            requires the `TAIPY_READER` role.

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
      description: |
        Creates a new data node from the *config_id* given as parameter.

        !!! Example

            === "Curl"
                ```shell
                    curl -X POST http://localhost:5000/api/v1/datanodes?config_id=historical_data_set
                ```
                In this example the REST API is served on port 5000 on localhost. We are using curl command line
                client.

                In this example the *config_id* value ("historical_data_set") is given as parameter directly in the
                url. A corresponding `DataNodeConfig^` must exist and must have been configured before.

                Here is the output message example:
                ```
                {"msg": "datanode created",
                "datanode": {
                    "default_path": null,
                    "path": "daily-min-temperatures.csv",
                    "name": null,
                    "storage_type": "csv",
                    "scope": 2,
                    "has_header": true}
                }
                ```

            === "Python"
                This Python example requires the 'requests' package to be installed (`pip install requests`).
                ```python
                import requests
                response = requests.post("http://localhost:5000/api/v1/datanodes?config_id=historical_data_set")
                print(response)
                print(response.json())
                ```
                In this example the *config_id* value ("historical_data_set") is given as parameter directly in the
                url. A corresponding `DataNodeConfig^` must exist and must have been configured before.

                Here is the output example:
                ```
                <Response [201]>
                {'msg': 'datanode created',
                'datanode': {
                    'name': None,
                    'scope': 2,
                    'path': 'daily-min-temperatures.csv',
                    'storage_type': 'csv',
                    'default_path': None,
                    'has_header': True}}
                ```

        !!! Note
            When the authorization feature is activated (available in Taipy Enterprise edition only), this endpoint
            requires the `TAIPY_EDITOR` role.

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
                  message:
                    type: string
                    description: Status message.
                  datanode: DataNodeSchema
    """

    def __init__(self, **kwargs):
        self.logger = kwargs.get("logger")

    def fetch_config(self, config_id):
        if config := Config.data_nodes.get(config_id):
            return config

        raise NonExistingDataNodeConfig(config_id)

    @_middleware
    def get(self):
        schema = DataNodeSchema(many=True)
        manager = _DataManagerFactory._build_manager()
        datanodes = [_to_model(REPOSITORY, datanode) for datanode in manager._get_all()]
        return schema.dump(datanodes)

    @_middleware
    def post(self):
        args = request.args
        config_id = args.get("config_id")

        if not config_id:
            raise ConfigIdMissingException

        config = self.fetch_config(config_id)
        schema = ds_schema_map.get(config.storage_type)()
        manager = _DataManagerFactory._build_manager()
        manager._bulk_get_or_create({config})
        return {
            "message": "Data node was created.",
            "datanode": schema.dump(config),
        }, 201


class DataNodeReader(Resource):
    """Single object resource

    ---
    get:
      tags:
        - api
      description: |
        Returns the data read from the data node identified by *datanode_id*. If the data node does not exist,
        a 404 error is returned.

        !!! Example

            === "Curl"

                ```shell
                  curl -X GET \
                  http://localhost:5000/api/v1/datanodes/DATANODE_historical_data_set_9db1b542-2e45-44e7-8a85-03ef9ead173d/read
                ```

                `DATANODE_historical_data_set_9db1b542-2e45-44e7-8a85-03ef9ead173d` is the *datanode_id*
                parameter. It represents the identifier of the data node to read.

                Here is an output example. In this case, the storage type of the data node to read is `csv`,
                and no exposed type is specified. The data is exposed as a list of dictionaries, each dictionary
                representing a raw of the csv file.
                ```
                {"data": [
                    {"Date": "1981-01-01", "Temp": 20.7}, {"Date": "1981-01-02", "Temp": 17.9},
                    {"Date": "1981-01-03", "Temp": 18.8}, {"Date": "1981-01-04", "Temp": 14.6},
                    {"Date": "1981-01-05", "Temp": 15.8}, {"Date": "1981-01-06", "Temp": 15.8},
                    {"Date": "1981-01-07", "Temp": 15.8}
                    ]}
                ```

            === "Python"
                This Python example requires the 'requests' package to be installed (`pip install requests`).
                ```python
                import requests
                response = requests.get(
                "http://localhost:5000/api/v1/datanodes/DATANODE_historical_data_set_9db1b542-2e45-44e7-8a85-03ef9ead173d/read")
                print(response)
                print(response.json())
                ```
                `DATANODE_historical_data_set_9db1b542-2e45-44e7-8a85-03ef9ead173d` is the *datanode_id*
                parameter. It represents the identifier of the data node to read.

                Here is an output example. In this case, the storage type of the data node to read is `csv`,
                and no exposed type is specified. The data is exposed as a list of dictionaries, each dictionary
                representing a raw of the csv file.
                ```
                {"data": [
                    {"Date": "1981-01-01", "Temp": 20.7}, {"Date": "1981-01-02", "Temp": 17.9},
                    {"Date": "1981-01-03", "Temp": 18.8}, {"Date": "1981-01-04", "Temp": 14.6},
                    {"Date": "1981-01-05", "Temp": 15.8}, {"Date": "1981-01-06", "Temp": 15.8},
                    {"Date": "1981-01-07", "Temp": 15.8}
                    ]}
                ```

        !!! Note
            When the authorization feature is activated (available in Taipy Enterprise edition only), this endpoint
            requires the `TAIPY_READER` role.

      parameters:
        - in: path
          name: datanode_id
          schema:
            type: string
          description: The id of the data node to read.
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
                  data:
                    type: Any
                    description: The data read from the data node.
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
        data = request.get_json(silent=True)
        data_node = _get_or_raise(datanode_id)
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
        Write data from request body into a data node by *datanode_id*. If the data node does not exist, a 404 error is
        returned.

        !!! Note
          When the authorization feature is activated (available in the **Enterprise** edition only), this endpoint
          requires `TAIPY_EDITOR` role.

        Code example:

        ```shell
          curl -X PUT -d '[{"path": "/abc", "type": 1}, {"path": "/def", "type": 2}]' \\
          -H 'Content-Type: application/json' \\
           http://localhost:5000/api/v1/datanodes/DATANODE_my_config_75750ed8-4e09-4e00-958d-e352ee426cc9/write
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
                  message:
                    type: string
                    description: Status message.
        404:
          description: No data node has the *datanode_id* identifier.
    """

    def __init__(self, **kwargs):
        self.logger = kwargs.get("logger")

    @_middleware
    def put(self, datanode_id):
        data = request.json
        data_node = _get_or_raise(datanode_id)
        data_node.write(data)
        return {"message": f"Data node {datanode_id} was successfully written."}
