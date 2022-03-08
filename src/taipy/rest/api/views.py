from flask import Blueprint, current_app, jsonify
from flask_restful import Api
from marshmallow import ValidationError

from ..extensions import apispec
from .resources import (
    CycleList,
    CycleResource,
    DataNodeList,
    DataNodeReader,
    DataNodeResource,
    DataNodeWriter,
    JobList,
    JobResource,
    PipelineExecutor,
    PipelineList,
    PipelineResource,
    ScenarioExecutor,
    ScenarioList,
    ScenarioResource,
    TaskExecutor,
    TaskList,
    TaskResource,
)
from .schemas import (
    CycleSchema,
    DataNodeSchema,
    JobSchema,
    PipelineSchema,
    ScenarioSchema,
    TaskSchema,
)

blueprint = Blueprint("api", __name__, url_prefix="/api/v1")

api = Api(blueprint)

api.add_resource(
    DataNodeResource,
    "/datanodes/<string:datanode_id>",
    endpoint="datanode_by_id",
)

api.add_resource(
    DataNodeReader,
    "/datanodes/<string:datanode_id>/read",
    endpoint="datanode_reader",
)

api.add_resource(
    DataNodeWriter,
    "/datanodes/<string:datanode_id>/write",
    endpoint="datanode_writer",
)

api.add_resource(DataNodeList, "/datanodes", endpoint="datanodes")

api.add_resource(
    TaskResource,
    "/tasks/<string:task_id>",
    endpoint="task_by_id",
)
api.add_resource(TaskList, "/tasks", endpoint="tasks")
api.add_resource(TaskExecutor, "/tasks/submit/<string:task_id>", endpoint="task_submit")

api.add_resource(
    PipelineResource,
    "/pipelines/<string:pipeline_id>",
    endpoint="pipeline_by_id",
)
api.add_resource(PipelineList, "/pipelines", endpoint="pipelines")
api.add_resource(
    PipelineExecutor,
    "/pipelines/submit/<string:pipeline_id>",
    endpoint="pipeline_submit",
)

api.add_resource(
    ScenarioResource,
    "/scenarios/<string:scenario_id>",
    endpoint="scenario_by_id",
)
api.add_resource(ScenarioList, "/scenarios", endpoint="scenarios")
api.add_resource(
    ScenarioExecutor,
    "/scenarios/submit/<string:scenario_id>",
    endpoint="scenario_submit",
)

api.add_resource(
    CycleResource,
    "/cycles/<string:cycle_id>",
    endpoint="cycle_by_id",
)
api.add_resource(CycleList, "/cycles", endpoint="cycles")

api.add_resource(
    JobResource,
    "/jobs/<string:job_id>",
    endpoint="job_by_id",
)
api.add_resource(JobList, "/jobs", endpoint="jobs")


@blueprint.before_app_first_request
def register_views():
    apispec.spec.components.schema("DataNodeSchema", schema=DataNodeSchema)
    apispec.spec.path(view=DataNodeResource, app=current_app)
    apispec.spec.path(view=DataNodeList, app=current_app)

    apispec.spec.components.schema("TaskSchema", schema=TaskSchema)
    apispec.spec.path(view=TaskResource, app=current_app)
    apispec.spec.path(view=TaskList, app=current_app)
    apispec.spec.path(view=TaskExecutor, app=current_app)

    apispec.spec.components.schema("PipelineSchema", schema=PipelineSchema)
    apispec.spec.path(view=PipelineResource, app=current_app)
    apispec.spec.path(view=PipelineList, app=current_app)
    apispec.spec.path(view=PipelineExecutor, app=current_app)

    apispec.spec.components.schema("ScenarioSchema", schema=ScenarioSchema)
    apispec.spec.path(view=ScenarioResource, app=current_app)
    apispec.spec.path(view=ScenarioList, app=current_app)
    apispec.spec.path(view=ScenarioExecutor, app=current_app)

    apispec.spec.components.schema("CycleSchema", schema=CycleSchema)
    apispec.spec.path(view=CycleResource, app=current_app)
    apispec.spec.path(view=CycleList, app=current_app)

    apispec.spec.components.schema("JobSchema", schema=JobSchema)
    apispec.spec.path(view=JobResource, app=current_app)
    apispec.spec.path(view=JobList, app=current_app)


@blueprint.errorhandler(ValidationError)
def handle_marshmallow_error(e):
    """Return json error for marshmallow validation errors.

    This will avoid having to try/catch ValidationErrors in all endpoints, returning
    correct JSON response with associated HTTP 400 Status (https://tools.ietf.org/html/rfc7231#section-6.5.1)
    """
    return jsonify(e.messages), 400
