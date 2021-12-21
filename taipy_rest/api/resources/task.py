from flask import jsonify, make_response, request
from flask_restful import Resource

from taipy.task.manager import TaskManager
from taipy.data.manager.data_manager import DataManager
from taipy.exceptions.repository import ModelNotFound

from taipy_rest.api.schemas import TaskSchema
from taipy.task.task import Task
from taipy.common.utils import load_fct


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
          description: task does not exists
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
          description: task does not exists
    """

    def get(self, task_id):
        try:
            schema = TaskSchema()
            manager = TaskManager()
            task = manager.get(task_id)
            return {"task": schema.dump(task)}
        except ModelNotFound:
            return make_response(jsonify({"message": f"Task {task_id} not found"}), 404)

    def delete(self, task_id):
        manager = TaskManager()
        manager.delete(task_id)

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
              TaskConfigSchema
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
                  task: TaskConfigSchema
    """

    def get(self):
        schema = TaskSchema(many=True)
        manager = TaskManager()
        tasks = manager.get_all()
        return schema.dump(tasks)

    def post(self):
        schema = TaskSchema()
        manager = TaskManager()
        data = schema.load(request.json)
        task = self.__create_task_from_schema(data)
        manager.repository.save(task)

        return {
            "msg": "task created",
            "task": schema.dump(data),
        }, 201

    def __create_task_from_schema(self, task_schema: TaskSchema):
        data_manager = DataManager()
        return Task(
            task_schema.config_name,
            [data_manager.get(ds) for ds in task_schema.input_ids],
            load_fct(task_schema.function_module, task_schema.function_name),
            [data_manager.get(ds) for ds in task_schema.output_ids],
            task_schema.parent_id,
        )
