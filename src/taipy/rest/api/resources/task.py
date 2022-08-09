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

from flask import jsonify, make_response, request
from flask_restful import Resource

from taipy.config.config import Config
from taipy.core.common._utils import _load_fct
from taipy.core.data._data_manager_factory import _DataManagerFactory
from taipy.core.task._task_manager_factory import _TaskManagerFactory
from taipy.core.task.task import Task

from ...commons.to_from_model import _to_model
from ..middlewares._middleware import _middleware
from ..schemas import TaskSchema

REPOSITORY = "task"


class TaskResource(Resource):
    """Single object resource

    ---
    get:
      tags:
        - api
      summary: Get a task.
      description: |
        Return a single task by *task_id*. If the task does not exist, a 404 error is returned.

        !!! Note
          When the authorization feature is activated (available in the **Enterprise** edition only), this endpoint requires `TAIPY_READER` role.

        Code example:

        ```shell
          curl -X GET http://localhost:5000/api/v1/tasks/TASK_my_config_75750ed8-4e09-4e00-958d-e352ee426cc9
        ```

      parameters:
        - in: path
          name: task_id
          schema:
            type: string
          description: The identifier of the task.
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  task: TaskSchema
        404:
          description: No task has the *task_id* identifier.
    delete:
      tags:
        - api
      summary: Delete a task.
      description: |
        Delete a task. If the task does not exist, a 404 error is returned.

        !!! Note
          When the authorization feature is activated (available in the **Enterprise** edition only), this endpoint requires `TAIPY_EDITOR` role.

        Code example:

        ```shell
          curl -X DELETE http://localhost:5000/api/v1/tasks/TASK_my_config_75750ed8-4e09-4e00-958d-e352ee426cc9
        ```
      parameters:
        - in: path
          name: task_id
          schema:
            type: string
          description: The identifier of the task.
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
          description: No task has the *task_id* identifier.
    """

    def __init__(self, **kwargs):
        self.logger = kwargs.get("logger")

    @_middleware
    def get(self, task_id):
        schema = TaskSchema()
        manager = _TaskManagerFactory._build_manager()
        task = manager._get(task_id)
        if not task:
            return make_response(jsonify({"message": f"Task {task_id} not found"}), 404)
        return {"task": schema.dump(_to_model(REPOSITORY, task))}

    @_middleware
    def delete(self, task_id):
        manager = _TaskManagerFactory._build_manager()
        task = manager._get(task_id)
        if not task:
            return make_response(jsonify({"message": f"Task {task_id} not found"}), 404)
        manager._delete(task_id)
        return {"msg": f"Task {task_id} deleted."}


class TaskList(Resource):
    """Creation and get_all

    ---
    get:
      tags:
        - api
      summary: Get all tasks.
      description: |
        Return an array of all tasks.

        !!! Note
          When the authorization feature is activated (available in the **Enterprise** edition only), this endpoint requires `TAIPY_READER` role.

        Code example:

        ```shell
          curl -X GET http://localhost:5000/api/v1/tasks
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
                          $ref: '#/components/schemas/TaskSchema'
    post:
      tags:
        - api
      summary: Create a task.
      description: |
        Create a new task from its *config_id*. If the config does not exist, a 404 error is returned.

        !!! Note
          When the authorization feature is activated (available in the **Enterprise** edition only), this endpoint requires `TAIPY_EDITOR` role.

        Code example:

        ```shell
          curl -X POST http://localhost:5000/api/v1/tasks?config_id=my_task_config
        ```
      parameters:
        - in: query
          name: config_id
          schema:
            type: string
          description: The identifier of the task configuration.
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
                  task: TaskSchema
    """

    def __init__(self, **kwargs):
        self.logger = kwargs.get("logger")

    def fetch_config(self, config_id):
        return Config.tasks[config_id]

    @_middleware
    def get(self):
        schema = TaskSchema(many=True)
        manager = _TaskManagerFactory._build_manager()
        tasks = [_to_model(REPOSITORY, task) for task in manager._get_all()]
        return schema.dump(tasks)

    @_middleware
    def post(self):
        args = request.args
        config_id = args.get("config_id")

        schema = TaskSchema()
        manager = _TaskManagerFactory._build_manager()
        if not config_id:
            return {"msg": "Config id is mandatory"}, 400

        try:
            config = self.fetch_config(config_id)
            task = manager._bulk_get_or_create([config])[0]

            return {
                "msg": "Task created.",
                "task": schema.dump(_to_model(REPOSITORY, task)),
            }, 201
        except KeyError:
            return {"msg": f"Config id {config_id} not found"}, 404


class TaskExecutor(Resource):
    """Execute a task

    ---
    post:
      tags:
        - api
      summary: Execute a task.
      description: |
        Execute a task by *task_id*. If the task does not exist, a 404 error is returned.

        !!! Note
          When the authorization feature is activated (available in the **Enterprise** edition only), this endpoint requires `TAIPY_EXECUTOR` role.

        Code example:

        ```shell
          curl -X POST http://localhost:5000/api/v1/tasks/submit/TASK_my_config_75750ed8-4e09-4e00-958d-e352ee426cc9
        ```

      parameters:
        - in: path
          name: task_id
          schema:
            type: string
      responses:
        204:
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    description: Status message.
                  task: TaskSchema
        404:
          description: No task has the *task_id* identifier.
    """

    def __init__(self, **kwargs):
        self.logger = kwargs.get("logger")

    @_middleware
    def post(self, task_id):
        manager = _TaskManagerFactory._build_manager()
        task = manager._get(task_id)
        if not task:
            return make_response(jsonify({"message": f"Task {task_id} not found"}), 404)
        manager._scheduler().submit_task(task)
        return {"message": f"Executed task {task_id}"}
