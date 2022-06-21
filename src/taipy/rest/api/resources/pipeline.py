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

from taipy.core.config.config import Config
from taipy.core.exceptions.exceptions import ModelNotFound, NonExistingPipeline
from taipy.core.pipeline._pipeline_manager_factory import _PipelineManagerFactory
from taipy.core.pipeline.pipeline import Pipeline
from taipy.core.task._task_manager_factory import _TaskManagerFactory

from ...commons.to_from_model import to_model
from ..middlewares._middleware import _middleware
from ..schemas import PipelineResponseSchema, PipelineSchema

REPOSITORY = "pipeline"


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

    def __init__(self, **kwargs):
        self.logger = kwargs.get("logger")

    @_middleware
    def get(self, pipeline_id):
        schema = PipelineResponseSchema()
        manager = _PipelineManagerFactory._build_manager()
        pipeline = manager._get(pipeline_id)
        if not pipeline:
            return make_response(jsonify({"message": f"Pipeline {pipeline_id} not found"}), 404)
        return {"pipeline": schema.dump(to_model(REPOSITORY, pipeline))}

    @_middleware
    def delete(self, pipeline_id):
        try:
            manager = _PipelineManagerFactory._build_manager()
            manager._delete(pipeline_id)
        except ModelNotFound:
            return make_response(jsonify({"message": f"DataNode {pipeline_id} not found"}), 404)

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

    def __init__(self, **kwargs):
        self.logger = kwargs.get("logger")

    def fetch_config(self, config_id):
        return Config.pipelines[config_id]

    @_middleware
    def get(self):
        schema = PipelineResponseSchema(many=True)
        manager = _PipelineManagerFactory._build_manager()
        pipelines = [to_model(REPOSITORY, pipeline) for pipeline in manager._get_all()]
        return schema.dump(pipelines)

    @_middleware
    def post(self):
        args = request.args
        config_id = args.get("config_id")

        response_schema = PipelineResponseSchema()
        manager = _PipelineManagerFactory._build_manager()
        if not config_id:
            return {"msg": "Config id is mandatory"}, 400

        try:
            config = self.fetch_config(config_id)
            pipeline = manager._get_or_create(config)

            return {
                "msg": "pipeline created",
                "pipeline": response_schema.dump(to_model(REPOSITORY, pipeline)),
            }, 201
        except KeyError:
            return {"msg": f"Config id {config_id} not found"}, 404

    def __create_pipeline_from_schema(self, pipeline_schema: PipelineSchema):
        task_manager = _TaskManagerFactory._build_manager()
        return Pipeline(
            config_id=pipeline_schema.get("name"),
            properties=pipeline_schema.get("properties", {}),
            tasks=[task_manager._get(ts) for ts in pipeline_schema.get("task_ids")],
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

    def __init__(self, **kwargs):
        self.logger = kwargs.get("logger")

    @_middleware
    def post(self, pipeline_id):
        try:
            manager = _PipelineManagerFactory._build_manager()
            manager._submit(pipeline_id)
            return {"message": f"Executed pipeline {pipeline_id}"}
        except NonExistingPipeline:
            return make_response(jsonify({"message": f"Pipeline {pipeline_id} not found"}), 404)
