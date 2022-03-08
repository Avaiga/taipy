import importlib
import os

from flask import jsonify, make_response, request
from flask_restful import Resource
from taipy.core.common._utils import _load_fct
from taipy.core.data._data_manager import _DataManager as DataManager
from taipy.core.exceptions.repository import ModelNotFound
from taipy.core.scheduler.scheduler import Scheduler
from taipy.core.task.task import Task
from taipy.core.task._task_manager import _TaskManager as TaskManager
from ...config import TAIPY_SETUP_FILE
from ..schemas import TaskSchema


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

    def get(self, task_id):
        schema = TaskSchema()
        manager = TaskManager()
        task = manager._get(task_id)
        if not task:
            return make_response(jsonify({"message": f"Task {task_id} not found"}), 404)
        return {"task": schema.dump(task)}

    def delete(self, task_id):
        try:
            manager = TaskManager()
            manager._delete(task_id)
        except ModelNotFound:
            return make_response(
                jsonify({"message": f"DataNode {task_id} not found"}), 404
            )

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
        schema = TaskSchema(many=True)
        manager = TaskManager()
        tasks = manager._get_all()
        return schema.dump(tasks)

    def post(self):
        args = request.args
        config_id = args.get("config_id")

        schema = TaskSchema()
        manager = TaskManager()
        if not config_id:
            return {"msg": "Config id is mandatory"}, 400

        try:
            config = self.fetch_config(config_id)
            task = manager._get_or_create(config)

            return {
                "msg": "task created",
                "task": schema.dump(task),
            }, 201
        except AttributeError:
            return {"msg": f"Config id {config_id} not found"}, 404

    def __create_task_from_schema(self, task_schema: TaskSchema):
        data_manager = DataManager()
        return Task(
            task_schema.get("config_id"),
            _load_fct(
                task_schema.get("function_module"), task_schema.get("function_name")
            ),
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

    def post(self, task_id):
        manager = TaskManager()
        task = manager._get(task_id)
        if not task:
            return make_response(jsonify({"message": f"Task {task_id} not found"}), 404)
        Scheduler().submit_task(task)
        return {"message": f"Executed task {task_id}"}
