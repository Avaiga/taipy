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

from taipy.config.config import Config
from taipy.core import Job
from taipy.core.common.alias import JobId
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
      summary: Get a job.
      description: |
        Return a single job by *job_id*. If the job does not exist, a 404 error is returned.

        !!! Note
          When the authorization feature is activated (available in the **Enterprise** edition only), the endpoint requires `TAIPY_READER` role.

        Code example:

        ```shell
          curl -X GET http://localhost:5000/api/v1/jobs/JOB_my_task_config_75750ed8-4e09-4e00-958d-e352ee426cc9
        ```

      parameters:
        - in: path
          name: job_id
          schema:
            type: string
          description: The identifier of the job.
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  job: JobSchema
        404:
          description: No job has the *job_id* identifier.
    delete:
      tags:
        - api
      summary: Delete a job.
      description: |
        Delete a job. If the job does not exist, a 404 error is returned.

        !!! Note
          When the authorization feature is activated (available in the **Enterprise** edition only), the endpoint requires `TAIPY_EDITOR` role.

        Code example:

        ```shell
          curl -X DELETE http://localhost:5000/api/v1/jobs/JOB_my_task_config_75750ed8-4e09-4e00-958d-e352ee426cc9
        ```

      parameters:
        - in: path
          name: job_id
          schema:
            type: string
          description: The identifier of the job.
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
          description: No job has the *job_id* identifier.
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
        manager = _JobManagerFactory._build_manager()
        job = manager._get(job_id)
        if not job:
            return make_response(jsonify({"message": f"Job {job_id} not found"}), 404)
        manager._delete(job)
        return {"msg": f"Job {job_id} deleted."}


class JobList(Resource):
    """Creation and get_all

    ---
    get:
      tags:
        - api
      summary: Get all jobs.
      description: |
        Return an array of all jobs.

        !!! Note
          When the authorization feature is activated (available in the **Enterprise** edition only), the endpoint requires `TAIPY_READER` role.

        Code example:

        ```shell
          curl -X GET http://localhost:5000/api/v1/jobs
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
                          $ref: '#/components/schemas/JobSchema'
    post:
      tags:
        - api
      summary: Create a job.
      description: |
        Create a job from a task *config_id*. If the config does not exist, a 404 error is returned.

        !!! Note
          When the authorization feature is activated (available in the **Enterprise** edition only), the endpoint requires `TAIPY_EDITOR` role.

        Code example:

        ```shell
          curl -X POST http://localhost:5000/api/v1/jobs?task_id=TASK_my_config_75750ed8-4e09-4e00-958d-e352ee426cc9
        ```

      parameters:
        - in: query
          name: task_id
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
        task_config_id = args.get("task_id")

        if not task_config_id:
            return {"msg": "Task config_id is mandatory"}, 400

        manager = _JobManagerFactory._build_manager()
        schema = JobSchema()
        job = self.__create_job_from_schema(task_config_id)

        if not job:
            return {"msg": f"Task with config_id {task_config_id} not found"}, 404

        manager._set(job)

        return {
            "msg": "Job created.",
            "job": schema.dump(job),
        }, 201

    def __create_job_from_schema(self, task_config_id: str) -> Optional[Job]:
        task_manager = _TaskManagerFactory._build_manager()
        try:
            task = task_manager._bulk_get_or_create([self.fetch_config(task_config_id)])[0]
        except KeyError:
            return None

        return Job(id=JobId(f"JOB_{uuid.uuid4()}"), task=task, submit_id=f"SUBMISSION_{uuid.uuid4()}")


class JobExecutor(Resource):
    """Cancel a job

    ---
    post:
      tags:
        - api
      summary: Cancel a job.
      description: |
        Cancel a job by *job_id*. If the job does not exist, a 404 error is returned.

        !!! Note
          When the authorization feature is activated (available in the **Enterprise** edition only), the endpoint requires `TAIPY_EXECUTOR` role.

        Code example:

        ```shell
          curl -X POST http://localhost:5000/api/v1/jobs/cancel/JOB_my_task_config_75750ed8-4e09-4e00-958d-e352ee426cc9
        ```

      parameters:
        - in: path
          name: job_id
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
                  job: JobSchema
        404:
          description: No job has the *job_id* identifier.
    """

    def __init__(self, **kwargs):
        self.logger = kwargs.get("logger")

    @_middleware
    def post(self, job_id):
        manager = _JobManagerFactory._build_manager()
        job = manager._get(job_id)
        if not job:
            return make_response(jsonify({"message": f"Job {job_id} not found"}), 404)
        manager._cancel(job)
        return {"message": f"Cancelled job {job_id}"}
