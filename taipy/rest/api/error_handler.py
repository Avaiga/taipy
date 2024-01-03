# Copyright 2021-2024 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

from flask import jsonify
from marshmallow import ValidationError

from taipy.core.exceptions.exceptions import (
    NonExistingCycle,
    NonExistingDataNode,
    NonExistingDataNodeConfig,
    NonExistingJob,
    NonExistingScenario,
    NonExistingScenarioConfig,
    NonExistingSequence,
    NonExistingSequenceConfig,
    NonExistingTask,
    NonExistingTaskConfig,
)

from .exceptions.exceptions import ConfigIdMissingException, ScenarioIdMissingException, SequenceNameMissingException
from .views import blueprint


def _create_404(e):
    return {"message": e.message}, 404


@blueprint.errorhandler(ValidationError)
def handle_marshmallow_error(e):
    """Return json error for marshmallow validation errors.

    This will avoid having to try/catch ValidationErrors in all endpoints, returning
    correct JSON response with associated HTTP 400 Status (https://tools.ietf.org/html/rfc7231#section-6.5.1)
    """
    return jsonify(e.messages), 400


@blueprint.errorhandler(ConfigIdMissingException)
def handle_config_id_missing_exception(e):
    return jsonify({"message": e.message}), 400


@blueprint.errorhandler(ScenarioIdMissingException)
def handle_scenario_id_missing_exception(e):
    return jsonify({"message": e.message}), 400


@blueprint.errorhandler(SequenceNameMissingException)
def handle_sequence_name_missing_exception(e):
    return jsonify({"message": e.message}), 400


@blueprint.errorhandler(NonExistingDataNode)
def handle_data_node_not_found(e):
    return _create_404(e)


@blueprint.errorhandler(NonExistingDataNodeConfig)
def handle_data_node_config_not_found(e):
    return _create_404(e)


@blueprint.errorhandler(NonExistingCycle)
def handle_cycle_not_found(e):
    return _create_404(e)


@blueprint.errorhandler(NonExistingJob)
def handle_job_not_found(e):
    return _create_404(e)


@blueprint.errorhandler(NonExistingSequence)
def handle_sequence_not_found(e):
    return _create_404(e)


@blueprint.errorhandler(NonExistingSequenceConfig)
def handle_sequence_config_not_found(e):
    return _create_404(e)


@blueprint.errorhandler(NonExistingScenario)
def handle_scenario_not_found(e):
    return _create_404(e)


@blueprint.errorhandler(NonExistingScenarioConfig)
def handle_scenario_config_not_found(e):
    return _create_404(e)


@blueprint.errorhandler(NonExistingTask)
def handle_task_not_found(e):
    return _create_404(e)


@blueprint.errorhandler(NonExistingTaskConfig)
def handle_task_config_not_found(e):
    return _create_404(e)
