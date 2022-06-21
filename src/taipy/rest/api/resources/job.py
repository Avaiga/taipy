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

import uuid
from typing import Optional

from flask import jsonify, make_response, request
from flask_restful import Resource

from taipy.core import Job
from taipy.core.common.alias import JobId
from taipy.core.config.config import Config
from taipy.core.exceptions.exceptions import ModelNotFound
from taipy.core.job._job_manager_factory import _JobManagerFactory
from taipy.core.task._task_manager_factory import _TaskManagerFactory

from ..middlewares._middleware import _middleware
from ..schemas import JobSchema


class JobResource(Resource):
    """Single object resource

    ---
    get:
      tags:
        - api
      summary: Get a job
      description: Get a single job by ID
      parameters:
        - in: path
          name: job_id
          schema:
            type: string
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  job: JobSchema
        404:
          description: job does not exist
    delete:
      tags:
        - api
      summary: Delete a job
      description: Delete a single job by ID
      parameters:
        - in: path
          name: job_id
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
                    example: job deleted
        404:
          description: job does not exist
    """

    def __init__(self, **kwargs):
        self.logger = kwargs.get("logger")

    @_middleware
    def get(self, job_id):
        schema = JobSchema()
        manager = _JobManagerFactory._build_manager()
        job = manager._get(job_id)
        if not job:
            return make_response(jsonify({"message": f"Job {job_id} not found"}), 404)
        return {"job": schema.dump(job)}

    @_middleware
    def delete(self, job_id):
        try:
            manager = _JobManagerFactory._build_manager()
            manager._delete(job_id)
        except ModelNotFound:
            return make_response(jsonify({"message": f"DataNode {job_id} not found"}), 404)

        return {"msg": f"job {job_id} deleted"}


class JobList(Resource):
    """Creation and get_all

    ---
    get:
      tags:
        - api
      summary: Get a list of jobs
      description: Get a list of paginated jobs
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
                          $ref: '#/components/schemas/JobSchema'
    post:
      tags:
        - api
      summary: Create a job
      description: Create a new job
      requestBody:
        content:
          application/json:
            schema:
              JobSchema
      responses:
        201:
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    example: job created
                  job: JobSchema
    """

    def __init__(self, **kwargs):
        self.logger = kwargs.get("logger")

    def fetch_config(self, config_id):
        return Config.tasks[config_id]

    @_middleware
    def get(self):
        schema = JobSchema(many=True)
        manager = _JobManagerFactory._build_manager()
        jobs = manager._get_all()
        return schema.dump(jobs)

    @_middleware
    def post(self):
        args = request.args
        task_name = args.get("task_name")

        if not task_name:
            return {"msg": "Config id is mandatory"}, 400

        manager = _JobManagerFactory._build_manager()
        schema = JobSchema()
        job = self.__create_job_from_schema(task_name)

        if not job:
            return {"msg": f"Task with name {task_name} not found"}, 404

        manager._set(job)

        return {
            "msg": "job created",
            "job": schema.dump(job),
        }, 201

    def __create_job_from_schema(self, task_name: str) -> Optional[Job]:
        task_manager = _TaskManagerFactory._build_manager()
        try:
            task = task_manager._bulk_get_or_create([self.fetch_config(task_name)])[0]
        except KeyError:
            return None

        return Job(id=JobId(f"JOB_{uuid.uuid4()}"), task=task)
