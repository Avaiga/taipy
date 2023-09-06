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


from flask import request
from flask_restful import Resource

from taipy.core.exceptions.exceptions import NonExistingScenario, NonExistingSequence
from taipy.core.scenario._scenario_manager_factory import _ScenarioManagerFactory
from taipy.core.sequence._sequence_manager_factory import _SequenceManagerFactory

from ...commons.to_from_model import _to_model
from ..exceptions.exceptions import ScenarioIdMissingException, SequenceNameMissingException
from ..middlewares._middleware import _middleware
from ..schemas import SequenceResponseSchema


def _get_or_raise(sequence_id: str):
    manager = _SequenceManagerFactory._build_manager()
    sequence = manager._get(sequence_id)
    if sequence is None:
        raise NonExistingSequence(sequence_id)
    return sequence


REPOSITORY = "sequence"


class SequenceResource(Resource):
    """Single object resource

    ---
    get:
      tags:
        - api
      summary: Get a sequence.
      description: |
        Return a single sequence by sequence_id. If the sequence does not exist, a 404 error is returned.

        !!! Note
          When the authorization feature is activated (available in the **Enterprise** edition only), this endpoint
          requires _TAIPY_READER_ role.

        Code example:

        ```shell
          curl -X GET http://localhost:5000/api/v1/sequences/SEQUENCE_my_config_75750ed8-4e09-4e00-958d-e352ee426cc9
        ```

      parameters:
        - in: path
          name: sequence_id
          schema:
            type: string
          description: The identifier of the sequence.
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  sequence: SequenceSchema
        404:
          description: No sequence has the *sequence_id* identifier.
    delete:
      tags:
        - api
      summary: Delete a sequence.
      description: |
        Delete a sequence. If the sequence does not exist, a 404 error is returned.

        !!! Note
          When the authorization feature is activated (available in the **Enterprise** edition only), this endpoint
          requires _TAIPY_EDITOR_ role.

        Code example:

        ```shell
          curl -X DELETE http://localhost:5000/api/v1/sequences/SEQUENCE_my_config_75750ed8-4e09-4e00-958d-e352ee426cc9
        ```

      parameters:
        - in: path
          name: sequence_id
          schema:
            type: string
          description: The identifier of the sequence.
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
          description: No sequence has the *sequence_id* identifier.
    """

    def __init__(self, **kwargs):
        self.logger = kwargs.get("logger")

    @_middleware
    def get(self, sequence_id):
        schema = SequenceResponseSchema()
        sequence = _get_or_raise(sequence_id)
        return {"sequence": schema.dump(_to_model(REPOSITORY, sequence))}

    @_middleware
    def delete(self, sequence_id):
        manager = _SequenceManagerFactory._build_manager()
        _get_or_raise(sequence_id)
        manager._delete(sequence_id)
        return {"message": f"Sequence {sequence_id} was deleted."}


class SequenceList(Resource):
    """Creation and get_all

    ---
    get:
      tags:
        - api
      summary: Get all sequences.
      description: |
        Return an array of all sequences.

        !!! Note
          When the authorization feature is activated (available in the **Enterprise** edition only), this endpoint
          requires _TAIPY_READER_ role.

        Code example:

        ```shell
          curl -X GET http://localhost:5000/api/v1/sequences
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
                          $ref: '#/components/schemas/SequenceSchema'
    post:
      tags:
        - api
      summary: Create a sequence.
      description: |
        Create a sequence from scenario_id, sequence_name and task_ids. If the scenario_id does not exist or sequence_name is not provided, a 404 error is returned.
        !!! Note
          When the authorization feature is activated (available in the **Enterprise** edition only), this endpoint
          requires _TAIPY_EDITOR_ role.

        Code example:

        ```shell
          curl -X POST --data '{"scenario_id": "SCENARIO_scenario_id", "sequence_name": "sequence", "tasks": []}' http://localhost:5000/api/v1/sequences
        ```

      parameters:
        - in: query
          name: scenario_id
          schema:
            type: string
          description: The Scenario the Sequence belongs to.
          name: sequence_name
          schema:
            type: string
          description: The name of the Sequence.
          name: tasks
          schema:
            type: list[string]
          description: A list of task id of the Sequence.

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
                  sequence: SequenceSchema
    """

    def __init__(self, **kwargs):
        self.logger = kwargs.get("logger")

    @_middleware
    def get(self):
        schema = SequenceResponseSchema(many=True)
        manager = _SequenceManagerFactory._build_manager()
        sequences = [_to_model(REPOSITORY, sequence) for sequence in manager._get_all()]
        return schema.dump(sequences)

    @_middleware
    def post(self):
        sequence_data = request.json
        scenario_id = sequence_data.get("scenario_id")
        sequence_name = sequence_data.get("sequence_name")
        sequence_task_ids = sequence_data.get("task_ids", [])

        response_schema = SequenceResponseSchema()
        if not scenario_id:
            raise ScenarioIdMissingException
        if not sequence_name:
            raise SequenceNameMissingException

        scenario = _ScenarioManagerFactory._build_manager()._get(scenario_id)
        if not scenario:
            raise NonExistingScenario(scenario_id=scenario_id)

        scenario.add_sequence(sequence_name, sequence_task_ids)
        sequence = scenario.sequences[sequence_name]

        return {
            "message": "Sequence was created.",
            "sequence": response_schema.dump(_to_model(REPOSITORY, sequence)),
        }, 201


class SequenceExecutor(Resource):
    """Execute a sequence

    ---
    post:
      tags:
        - api
      summary: Execute a sequence.
      description: |
        Execute a sequence from sequence_id. If the sequence does not exist, a 404 error is returned.

        !!! Note
          When the authorization feature is activated (available in the **Enterprise** edition only), This endpoint
          requires _TAIPY_EXECUTOR_ role.

        Code example:

        ```shell
          curl -X POST http://localhost:5000/api/v1/sequences/submit/SEQUENCE_my_config_75750ed8-4e09-4e00-958d-e352ee426cc9
        ```

      parameters:
        - in: path
          name: sequence_id
          schema:
            type: string
      responses:
        204:
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
                    description: Status message.
                  sequence: SequenceSchema
        404:
            description: No sequence has the *sequence_id* identifier.
    """

    def __init__(self, **kwargs):
        self.logger = kwargs.get("logger")

    @_middleware
    def post(self, sequence_id):
        _get_or_raise(sequence_id)
        manager = _SequenceManagerFactory._build_manager()
        manager._submit(sequence_id)
        return {"message": f"Sequence {sequence_id} was submitted."}
