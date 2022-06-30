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

from flask import Blueprint, current_app, jsonify
from flask_restful import Api
from marshmallow import ValidationError

from taipy.core.common._taipy_logger import _TaipyLogger
from taipy.core.common._utils import _load_fct

from ..extensions import apispec
from .middlewares._middleware import _using_enterprise
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
from .schemas import CycleSchema, DataNodeSchema, JobSchema, PipelineSchema, ScenarioSchema, TaskSchema

_logger = _TaipyLogger._get_logger()


blueprint = Blueprint("api", __name__, url_prefix="/api/v1")

api = Api(blueprint)

api.add_resource(
    DataNodeResource,
    "/datanodes/<string:datanode_id>",
    endpoint="datanode_by_id",
    resource_class_kwargs={"logger": _logger},
)

api.add_resource(
    DataNodeReader,
    "/datanodes/<string:datanode_id>/read",
    endpoint="datanode_reader",
    resource_class_kwargs={"logger": _logger},
)

api.add_resource(
    DataNodeWriter,
    "/datanodes/<string:datanode_id>/write",
    endpoint="datanode_writer",
    resource_class_kwargs={"logger": _logger},
)

api.add_resource(
    DataNodeList,
    "/datanodes",
    endpoint="datanodes",
    resource_class_kwargs={"logger": _logger},
)

api.add_resource(
    TaskResource,
    "/tasks/<string:task_id>",
    endpoint="task_by_id",
    resource_class_kwargs={"logger": _logger},
)
api.add_resource(TaskList, "/tasks", endpoint="tasks", resource_class_kwargs={"logger": _logger})
api.add_resource(
    TaskExecutor,
    "/tasks/submit/<string:task_id>",
    endpoint="task_submit",
    resource_class_kwargs={"logger": _logger},
)

api.add_resource(
    PipelineResource,
    "/pipelines/<string:pipeline_id>",
    endpoint="pipeline_by_id",
    resource_class_kwargs={"logger": _logger},
)
api.add_resource(
    PipelineList,
    "/pipelines",
    endpoint="pipelines",
    resource_class_kwargs={"logger": _logger},
)
api.add_resource(
    PipelineExecutor,
    "/pipelines/submit/<string:pipeline_id>",
    endpoint="pipeline_submit",
    resource_class_kwargs={"logger": _logger},
)

api.add_resource(
    ScenarioResource,
    "/scenarios/<string:scenario_id>",
    endpoint="scenario_by_id",
    resource_class_kwargs={"logger": _logger},
)
api.add_resource(
    ScenarioList,
    "/scenarios",
    endpoint="scenarios",
    resource_class_kwargs={"logger": _logger},
)
api.add_resource(
    ScenarioExecutor,
    "/scenarios/submit/<string:scenario_id>",
    endpoint="scenario_submit",
    resource_class_kwargs={"logger": _logger},
)

api.add_resource(
    CycleResource,
    "/cycles/<string:cycle_id>",
    endpoint="cycle_by_id",
    resource_class_kwargs={"logger": _logger},
)
api.add_resource(
    CycleList,
    "/cycles",
    endpoint="cycles",
    resource_class_kwargs={"logger": _logger},
)

api.add_resource(
    JobResource,
    "/jobs/<string:job_id>",
    endpoint="job_by_id",
    resource_class_kwargs={"logger": _logger},
)
api.add_resource(JobList, "/jobs", endpoint="jobs", resource_class_kwargs={"logger": _logger})


def load_enterprise_resources(api: Api):
    """
    Load enterprise resources.
    """

    if not _using_enterprise():
        return
    load_resources = _load_fct("taipy.enterprise.rest.api.views", "_load_resources")
    load_resources(api)


load_enterprise_resources(api)


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

    if _using_enterprise():
        _register_views = _load_fct("taipy.enterprise.rest.api.views", "_register_views")
        _register_views(apispec)


@blueprint.errorhandler(ValidationError)
def handle_marshmallow_error(e):
    """Return json error for marshmallow validation errors.

    This will avoid having to try/catch ValidationErrors in all endpoints, returning
    correct JSON response with associated HTTP 400 Status (https://tools.ietf.org/html/rfc7231#section-6.5.1)
    """
    return jsonify(e.messages), 400
