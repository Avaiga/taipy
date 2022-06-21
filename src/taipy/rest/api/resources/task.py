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

from taipy.core.common._utils import _load_fct
from taipy.core.config.config import Config
from taipy.core.data._data_manager_factory import _DataManagerFactory
from taipy.core.exceptions.exceptions import ModelNotFound
from taipy.core.task._task_manager_factory import _TaskManagerFactory
from taipy.core.task.task import Task

from ...commons.to_from_model import to_model
from ..middlewares._middleware import _middleware
from ..schemas import TaskSchema

REPOSITORY = "task"


class TaskResource(Resource):
    """Single object resource

    ---
    get:
      tags:
        - api
      summary: Get a task
      description: Get a single task by ID
      parameters:
        - in: path
          name: task_id
          schema:
            type: string
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  task: TaskSchema
        404:
          description: task does not exist
    delete:
      tags:
        - api
      summary: Delete a task
      description: Delete a single task by ID
      parameters:
        - in: path
          name: task_id
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
                    example: task deleted
        404:
          description: task does not exist
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
        return {"task": schema.dump(to_model(REPOSITORY, task))}

    @_middleware
    def delete(self, task_id):
        try:
            manager = _TaskManagerFactory._build_manager()
            manager._delete(task_id)
        except ModelNotFound:
            return make_response(jsonify({"message": f"DataNode {task_id} not found"}), 404)

        return {"msg": f"task {task_id} deleted"}


class TaskList(Resource):
    """Creation and get_all

    ---
    get:
      tags:
        - api
      summary: Get a list of tasks
      description: Get a list of paginated tasks
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
      summary: Create a task
      description: Create a new task
      requestBody:
        content:
          application/json:
            schema:
              TaskSchema
      responses:
        201:
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    example: task created
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
        tasks = [to_model(REPOSITORY, task) for task in manager._get_all()]
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
                "msg": "task created",
                "task": schema.dump(to_model(REPOSITORY, task)),
            }, 201
        except KeyError:
            return {"msg": f"Config id {config_id} not found"}, 404

    def __create_task_from_schema(self, task_schema: TaskSchema):
        data_manager = _DataManagerFactory._build_manager()
        return Task(
            task_schema.get("config_id"),
            _load_fct(task_schema.get("function_module"), task_schema.get("function_name")),
            [data_manager._get(ds) for ds in task_schema.get("input_ids")],
            [data_manager._get(ds) for ds in task_schema.get("output_ids")],
            task_schema.get("parent_id"),
        )


class TaskExecutor(Resource):
    """Execute a task

    ---
    post:
      tags:
        - api
      summary: Execute a task
      description: Execute a task
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
                    example: task created
                  task: TaskSchema
      404:
          description: task does not exist
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
