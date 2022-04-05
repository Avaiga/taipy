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
from taipy.core.job._job_manager import _JobManager as JobManager
from taipy.core.task._task_manager import _TaskManager as TaskManager

from ..schemas import JobResponseSchema, JobSchema


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

    def get(self, job_id):
        schema = JobResponseSchema()
        manager = JobManager()
        job = manager._get(job_id)
        if not job:
            return make_response(jsonify({"message": f"Job {job_id} not found"}), 404)
        return {"job": schema.dump(job)}

    def delete(self, job_id):
        try:
            manager = JobManager()
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

    def get(self):
        schema = JobResponseSchema(many=True)
        manager = JobManager()
        jobs = manager._get_all()
        return schema.dump(jobs)

    def post(self):
        schema = JobSchema()

        manager = JobManager()
        response_schema = JobResponseSchema()
        job_data = schema.load(request.json)
        job = self.__create_job_from_schema(job_data)

        if not job:
            return {"msg": f"Task with name {job_data.get('task_name')} not found"}, 404

        manager._set(job)

        return {
            "msg": "job created",
            "job": response_schema.dump(job),
        }, 201

    def __create_job_from_schema(self, job_schema: JobSchema) -> Optional[Job]:
        task_manager = TaskManager()
        try:
            task = task_manager._get_or_create(self.fetch_config(job_schema.get("task_name")))
        except KeyError:
            return None

        return Job(id=JobId(f"JOB_{uuid.uuid4()}"), task=task)
