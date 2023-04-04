# Copyright 2023 Avaiga Private Limited
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

from flask import request
from flask_restful import Resource

from taipy.config.common.frequency import Frequency
from taipy.core import Cycle
from taipy.core.cycle._cycle_manager_factory import _CycleManagerFactory
from taipy.core.exceptions.exceptions import NonExistingCycle

from ...commons.to_from_model import _to_model
from ..middlewares._middleware import _middleware
from ..schemas import CycleResponseSchema, CycleSchema

REPOSITORY = "cycle"


def _get_or_raise(cycle_id: str) -> None:
    manager = _CycleManagerFactory._build_manager()
    cycle = manager._get(cycle_id)
    if not cycle:
        raise NonExistingCycle(cycle_id)
    return cycle


class CycleResource(Resource):
    """Single object resource

    ---
    get:
      tags:
        - api
      description: |
        Returns a `CycleSchema^` representing the unique `Cycle^` identified by the *cycle_id*
        given as parameter. If no cycle corresponds to *cycle_id*, a `404` error is returned.

        !!! Example

            === "Curl"
                ```shell
                    curl -X GET http://localhost:5000/api/v1/cycles/CYCLE_223894_e0fab919-b50b-4b9f-ac09-52f77474fa7a
                ```
                In this example the REST API is served on port 5000 on localhost. We are using curl command line
                client.

                `CYCLE_223894_e0fab919-b50b-4b9f-ac09-52f77474fa7a` is the value of the *cycle_id* parameter. It
                represents the identifier of the Cycle we want to retrieve.

                In case of success here is an example of the response:
                ``` JSON
                {"cycle": {
                    "frequency": "Frequency.DAILY",
                    "creation_date": "2022-08-04T17:13:32.797384",
                    "id": "CYCLE_223894_e0fab919-b50b-4b9f-ac09-52f77474fa7a",
                    "start_date": "2022-08-04T00:00:00",
                    "end_date": "2022-08-04T23:59:59.999999",
                    "name": "Frequency.DAILY_2022-08-04T17:13:32.797384"
                ```

                In case of failure here is an example of the response:
                ``` JSON
                {"message": "Cycle CYCLE_223894_e0fab919-b50b-4b9f-ac09-52f77474fa7a not found."}
                ```

            === "Python"
                This Python example requires the 'requests' package to be installed (`pip install requests`).
                ```python
                import requests
                    response = requests.get("http://localhost:5000/api/v1/cycles/CYCLE_223894_e0fab919-b50b-4b9f-ac09-52f77474fa7a")
                    print(response)
                    print(response.json())
                ```
                `CYCLE_223894_e0fab919-b50b-4b9f-ac09-52f77474fa7a` is the value of the  *cycle_id* parameter. It
                represents the identifier of the Cycle we want to retrieve.

                In case of success here is an output example:
                ```
                <Response [200]>
                {'cycle': {
                    'frequency': 'Frequency.DAILY',
                    'creation_date': '2022-08-04T17:13:32.797384',
                    'id': 'CYCLE_223894_e0fab919-b50b-4b9f-ac09-52f77474fa7a',
                    'start_date': '2022-08-04T00:00:00',
                    'end_date': '2022-08-04T23:59:59.999999',
                    'name': 'Frequency.DAILY_2022-08-04T17:13:32.797384'
                ```

                In case of failure here is an output example:
                ```
                <Response [404]>
                {'message': 'Cycle CYCLE_223894_e0fab919-b50b-4b9f-ac09-52f77474fa7a not found.'}

                ```

        !!! Note
          When the authorization feature is activated (available in Taipy Enterprise edition only), this endpoint
            requires the `TAIPY_READER` role.

      parameters:
        - in: path
          name: cycle_id
          schema:
            type: string
          description: The identifier of the cycle to retrieve.
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  cycle: CycleSchema
        404:
          description: No cycle has the *cycle_id* identifier.
    delete:
      tags:
        - api
      description: |
        Deletes the `Cycle^` identified by the  *cycle_id* given as parameter. If the cycle does not exist,
        a 404 error is returned.

        !!! Example

            === "Curl"
                ```shell
                    curl -X DELETE http://localhost:5000/api/v1/cycles/CYCLE_223894_e0fab919-b50b-4b9f-ac09-52f77474fa7a
                ```
                In this example the REST API is served on port 5000 on localhost. We are using curl command line
                client.

                `CYCLE_223894_e0fab919-b50b-4b9f-ac09-52f77474fa7a` is the value of the  *cycle_id* parameter. It
                represents the identifier of the Cycle we want to delete.

                In case of success here is an example of the response:
                ``` JSON
                {"message": "Cycle CYCLE_223894_e0fab919-b50b-4b9f-ac09-52f77474fa7a was deleted."}
                ```

                In case of failure here is an example of the response:
                ``` JSON
                {"message": "Cycle CYCLE_223894_e0fab919-b50b-4b9f-ac09-52f77474fa7a not found."}
                ```

            === "Python"
                This Python example requires the 'requests' package to be installed (`pip install requests`).
                ```python
                import requests
                    response = requests.delete("http://localhost:5000/api/v1/cycles/CYCLE_797384_ef210412-af91-4f41-b6e8-74d1648edcba")
                    print(response)
                    print(response.json())
                ```
                `CYCLE_223894_e0fab919-b50b-4b9f-ac09-52f77474fa7a` is the value of the  *cycle_id* parameter. It
                represents the identifier of the Cycle we want to delete.

                In case of success here is an output example:
                ```
                <Response [200]>
                {"message": "Cycle CYCLE_223894_e0fab919-b50b-4b9f-ac09-52f77474fa7a was deleted."}
                ```

                In case of failure here is an output example:
                ```
                <Response [404]>
                {'message': 'Cycle CYCLE_223894_e0fab919-b50b-4b9f-ac09-52f77474fa7a not found.'}

                ```

        !!! Note
            When the authorization feature is activated (available in Taipy Enterprise edition only), this endpoint
            requires the `TAIPY_EDITOR` role.

      parameters:
        - in: path
          name: cycle_id
          schema:
            type: string
          description: The id of the cycle to delete.
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
          description: No cycle has the  *cycle_id* identifier.
    """

    def __init__(self, **kwargs):
        self.logger = kwargs.get("logger")

    @_middleware
    def get(self, cycle_id):
        schema = CycleResponseSchema()
        cycle = _get_or_raise(cycle_id)
        return {"cycle": schema.dump(_to_model(REPOSITORY, cycle))}

    @_middleware
    def delete(self, cycle_id):
        manager = _CycleManagerFactory._build_manager()
        _get_or_raise(cycle_id)
        manager._delete(cycle_id)
        return {"message": f"Cycle {cycle_id} was deleted."}


class CycleList(Resource):
    """Creation and get_all

    ---
    get:
      tags:
        - api
      description: |
        Returns a `CycleSchema^` list representing all existing Cycles.

        !!! Example

            === "Curl"
                ```shell
                    curl -X GET http://localhost:5000/api/v1/cycles
                ```
                In this example the REST API is served on port 5000 on localhost. We are using curl command line
                client.

                Here is an example of the response:
                ``` JSON
                [
                    {
                    "frequency": "Frequency.DAILY",
                    "end_date": "2022-08-06T23:59:59.999999",
                    "creation_date": "2022-08-06T15:45:50.223894",
                    "start_date": "2022-08-06T00:00:00",
                    "id": "CYCLE_223894_e0fab919-b50b-4b9f-ac09-52f77474fa7a",
                    "name": "Frequency.DAILY_2022-08-06T15:45:50.223894"
                    }
                ]
                ```

                If there is no cycle, the response is an empty list as follows:
                ``` JSON
                []
                ```

            === "Python"
                This Python example requires the 'requests' package to be installed (`pip install requests`).
                ```python
                import requests
                    response = requests.get("http://localhost:5000/api/v1/cycles")
                    print(response)
                    print(response.json())
                ```

                In case of success here is an output example:
                ```
                <Response [200]>
                [{
                    "frequency": "Frequency.DAILY",
                    "end_date": "2022-08-06T23:59:59.999999",
                    "creation_date": "2022-08-06T15:45:50.223894",
                    "start_date": "2022-08-06T00:00:00",
                    "id": "CYCLE_223894_e0fab919-b50b-4b9f-ac09-52f77474fa7a",
                    "name": "Frequency.DAILY_2022-08-06T15:45:50.223894"
                    }
                ]
                ```

                If there is no cycle, the response is an empty list as follows:
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
                          $ref: '#/components/schemas/CycleSchema'
    post:
      tags:
        - api
      description: |
        Creates a new cycle from the `CycleSchema^` given in the request body.

        !!! Example

            === "Curl"
                ```shell
                    curl -X POST -H "Content-Type: application/json"\
                    -d '{"frequency": "DAILY", "properties": {}, "creation_date": "2020-01-01T00:00:00",\
                    "start_date": "2020-01-01T00:00:00", "end_date": "2020-01-01T00:00:00"}'\
                    http://localhost:5000/api/v1/cycles
                ```
                In this example the REST API is served on port 5000 on localhost. We are using curl command line
                client.

                In the curl command line, a `CycleSchema^` is provided as JSON dictionary parameter with the curl
                option -d (--data) to specify the various attributes of the `Cycle^` to create:
                ``` JSON
                {
                    "frequency": "DAILY",
                    "properties": {},
                    "creation_date": "2020-01-01T00:00:00",
                    "start_date": "2020-01-01T00:00:00",
                    "end_date": "2020-01-01T00:00:00"
                }
                ```

            === "Python"
                This Python example requires the 'requests' package to be installed (`pip install requests`).
                ```python
                import requests
                    cycle_schema = {
                        "frequency": "DAILY",
                        "properties": {},
                        "creation_date": "2020-01-01T00:00:00",
                        "start_date": "2020-01-01T00:00:00",
                        "end_date": "2020-01-01T00:00:00"
                    }
                    response = requests.post("http://localhost:5000/api/v1/cycles", json=cycle_schema)
                    print(response)
                    print(response.json())
                ```
                A `CycleSchema^` is provided as a dictionary to specify the various attributes of the `Cycle^` to
                create.

                Here is the output example:
                ```
                <Response [201]>
                {
                    'message': 'Cycle was created.',
                    'cycle': {
                        'frequency': 'Frequency.DAILY',
                        'end_date': '2020-01-01T00:00:00',
                        'creation_date': '2020-01-01T00:00:00',
                        'start_date': '2020-01-01T00:00:00',
                        'id': 'CYCLE_c9cc527f-a8c8-4238-8f31-42166a9817db',
                        'name': 'Frequency.DAILY_2020-01-01T00:00:00',
                        'properties': {}}}
                ```

        !!! Note
            When the authorization feature is activated (available in Taipy Enterprise edition only), this endpoint
            requires the `TAIPY_EDITOR` role.

      requestBody:
        required: true
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
                  message:
                    type: string
                    description: Status message.
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
            "message": "Cycle was created.",
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
