import uuid
from typing import Optional

from flask import jsonify, make_response, request
from flask_restful import Resource
from taipy.common.alias import JobId

from taipy.job.job_manager import JobManager
from taipy.task.manager import TaskManager
from taipy.exceptions.job import NonExistingJob
from taipy.exceptions.repository import ModelNotFound

from taipy_rest.api.schemas import JobSchema, JobResponseSchema
from taipy.job.job import Job
from taipy_rest.config import TAIPY_SETUP_FILE
import importlib


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

    def get(self, job_id):
        try:
            schema = JobResponseSchema()
            manager = JobManager()
            job = manager.get(job_id)
            return {"job": schema.dump(manager.repository.to_model(job))}
        except NonExistingJob:
            return make_response(jsonify({"message": f"Job {job_id} not found"}), 404)

    def delete(self, job_id):
        try:
            manager = JobManager()
            manager.delete(job_id)
        except ModelNotFound:
            return make_response(
                jsonify({"message": f"DataNode {job_id} not found"}), 404
            )

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

    def __init__(self):
        spec = importlib.util.spec_from_file_location("taipy_setup", TAIPY_SETUP_FILE)
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)

    def fetch_config(self, config_name):
        return getattr(self.module, config_name)

    def get(self):
        schema = JobResponseSchema(many=True)
        manager = JobManager()
        jobs = manager.get_all()
        jobs_model = [manager.repository.to_model(t) for t in jobs]
        return schema.dump(jobs_model)

    def post(self):
        schema = JobSchema()

        manager = JobManager()
        response_schema = JobResponseSchema()
        job_data = schema.load(request.json)
        job = self.__create_job_from_schema(job_data)

        if not job:
            return {"msg": f"Task with name {job_data.get('task_name')} not found"}, 404

        manager.set(job)

        return {
            "msg": "job created",
            "job": response_schema.dump(manager.repository.to_model(job)),
        }, 201

    def __create_job_from_schema(self, job_schema: JobSchema) -> Optional[Job]:
        task_manager = TaskManager()
        try:
            task = task_manager.get_or_create(
                self.fetch_config(job_schema.get("task_name"))
            )
        except AttributeError:
            return None

        return Job(id=JobId(f"JOB_{uuid.uuid4()}"), task=task)
