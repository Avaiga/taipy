from flask import Blueprint, current_app, jsonify
from flask_restful import Api
from marshmallow import ValidationError

from taipy_rest.api.resources import (
    DataSourceList,
    DataSourceResource,
    TaskList,
    TaskResource,
    TaskExecutor,
    PipelineList,
    PipelineResource,
    PipelineExecutor,
)
from taipy_rest.api.schemas import DataSourceSchema, TaskSchema, PipelineSchema
from taipy_rest.extensions import apispec

blueprint = Blueprint("api", __name__, url_prefix="/api/v1")

api = Api(blueprint)

api.add_resource(
    DataSourceResource,
    "/datasources/<string:datasource_id>",
    endpoint="datasource_by_id",
)
api.add_resource(DataSourceList, "/datasources", endpoint="datasources")

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


@blueprint.before_app_first_request
def register_views():
    apispec.spec.components.schema("DataSourceSchema", schema=DataSourceSchema)
    apispec.spec.path(view=DataSourceResource, app=current_app)
    apispec.spec.path(view=DataSourceList, app=current_app)

    apispec.spec.components.schema("TaskSchema", schema=TaskSchema)
    apispec.spec.path(view=TaskResource, app=current_app)
    apispec.spec.path(view=TaskList, app=current_app)
    apispec.spec.path(view=TaskExecutor, app=current_app)

    apispec.spec.components.schema("PipelineSchema", schema=PipelineSchema)
    apispec.spec.path(view=PipelineResource, app=current_app)
    apispec.spec.path(view=PipelineList, app=current_app)
    apispec.spec.path(view=PipelineExecutor, app=current_app)


@blueprint.errorhandler(ValidationError)
def handle_marshmallow_error(e):
    """Return json error for marshmallow validation errors.

    This will avoid having to try/catch ValidationErrors in all endpoints, returning
    correct JSON response with associated HTTP 400 Status (https://tools.ietf.org/html/rfc7231#section-6.5.1)
    """
    return jsonify(e.messages), 400
