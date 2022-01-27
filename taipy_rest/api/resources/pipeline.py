from flask import jsonify, make_response, request
from flask_restful import Resource

from taipy.pipeline.manager import PipelineManager
from taipy.task.manager import TaskManager
from taipy.exceptions.pipeline import NonExistingPipeline
from taipy.exceptions.repository import ModelNotFound

from taipy_rest.api.schemas import PipelineSchema, PipelineResponseSchema
from taipy.pipeline.pipeline import Pipeline
from taipy_rest.config import TAIPY_SETUP_FILE
import importlib


class PipelineResource(Resource):
    """Single object resource

    ---
    get:
      tags:
        - api
      summary: Get a pipeline
      description: Get a single pipeline by ID
      parameters:
        - in: path
          name: pipeline_id
          schema:
            type: string
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  pipeline: PipelineSchema
        404:
          description: pipeline does not exist
    delete:
      tags:
        - api
      summary: Delete a pipeline
      description: Delete a single pipeline by ID
      parameters:
        - in: path
          name: pipeline_id
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
                    example: pipeline deleted
        404:
          description: pipeline does not exist
    """

    def get(self, pipeline_id):
        try:
            schema = PipelineResponseSchema()
            manager = PipelineManager()
            pipeline = manager.get(pipeline_id)
            return {"pipeline": schema.dump(manager.repository.to_model(pipeline))}
        except NonExistingPipeline:
            return make_response(
                jsonify({"message": f"Pipeline {pipeline_id} not found"}), 404
            )

    def delete(self, pipeline_id):
        try:
            manager = PipelineManager()
            manager.delete(pipeline_id)
        except ModelNotFound:
            return make_response(
                jsonify({"message": f"DataNode {pipeline_id} not found"}), 404
            )

        return {"msg": f"pipeline {pipeline_id} deleted"}


class PipelineList(Resource):
    """Creation and get_all

    ---
    get:
      tags:
        - api
      summary: Get a list of pipelines
      description: Get a list of paginated pipelines
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
                          $ref: '#/components/schemas/PipelineSchema'
    post:
      tags:
        - api
      summary: Create a pipeline
      description: Create a new pipeline
      requestBody:
        content:
          application/json:
            schema:
              PipelineSchema
      responses:
        201:
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    example: pipeline created
                  pipeline: PipelineSchema
    """

    def __init__(self):
        spec = importlib.util.spec_from_file_location("taipy_setup", TAIPY_SETUP_FILE)
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)

    def fetch_config(self, config_name):
        return getattr(self.module, config_name)

    def get(self):
        schema = PipelineResponseSchema(many=True)
        manager = PipelineManager()
        pipelines = manager.get_all()
        pipelines_model = [manager.repository.to_model(t) for t in pipelines]
        return schema.dump(pipelines_model)

    def post(self):
        args = request.args
        config_name = args.get("config_name")

        response_schema = PipelineResponseSchema()
        manager = PipelineManager()
        if not config_name:
            return {"msg": "Config name is mandatory"}, 400

        try:
            config = self.fetch_config(config_name)
            pipeline = manager.get_or_create(config)

            return {
                "msg": "pipeline created",
                "pipeline": response_schema.dump(manager.repository.to_model(pipeline)),
            }, 201
        except AttributeError:
            return {"msg": f"Config name {config_name} not found"}, 404

    def __create_pipeline_from_schema(self, pipeline_schema: PipelineSchema):
        task_manager = TaskManager()
        return Pipeline(
            config_name=pipeline_schema.get("name"),
            properties=pipeline_schema.get("properties", {}),
            tasks=[task_manager.get(ts) for ts in pipeline_schema.get("task_ids")],
            parent_id=pipeline_schema.get("parent_id"),
        )


class PipelineExecutor(Resource):
    """Execute a pipeline

    ---
    post:
      tags:
        - api
      summary: Execute a pipeline
      description: Execute a pipeline
      parameters:
        - in: path
          name: pipeline_id
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
                    example: pipeline created
                  pipeline: PipelineSchema
      404:
          description: pipeline does not exist
    """

    def post(self, pipeline_id):
        try:
            manager = PipelineManager()
            manager.submit(pipeline_id)
            return {"message": f"Executed pipeline {pipeline_id}"}
        except NonExistingPipeline:
            return make_response(
                jsonify({"message": f"Pipeline {pipeline_id} not found"}), 404
            )
