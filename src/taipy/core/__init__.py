# Copyright 2023 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

"""# Taipy Core

The Taipy Core package is a Python library designed to build powerful, customized, data-driven back-end
applications. It provides the tools to help Python developers transform their algorithms into a
complete back-end application.
More details on the [Taipy Core](../../../manuals/core/) functionalities are available in the user manual.

To build a Taipy Core application, the first step consists of setting up the Taipy configuration to design
your application's characteristics and behaviors.
Import `Config^` from the `taipy.config^` module, then use the various methods of the `Config^` singleton class to
configure your core application. In particular, configure the
[data nodes](../../../manuals/core/config/data-node-config), [tasks](../../../manuals/core/config/task-config),
and [scenarios](../../../manuals/core/config/scenario-config).
Please refer to the [Core configuration user manual](../../../manuals/core/config/) for more information and
detailed examples.

Once your application is configured, import module `import taipy as tp` so you can use any function described
in the following [function](./#functions) section. In particular, the most used functions are `tp.create_scenario`,
`tp.get_scenarios`, `tp.get_data_nodes`, `tp.submit`, used to get, create, and submit entities.

!!! Note

    Taipy Core provides a runnable service, `Core^` that runs as a service in a dedicated thread. The purpose is to
    have a dedicated thread responsible for dispatching the submitted jobs to an available executor for their execution.

    In particular, this `Core^` service is automatically run when Core is used with taipy-rest or taipy-gui. See the
    [running services](../../../manuals/running_services/) page of the user manual for more details.

"""
import json
import os

from ._core import Core
from .common.alias import CycleId, DataNodeId, Edit, JobId, PipelineId, ScenarioId, TaskId
from .common.default_custom_document import DefaultCustomDocument
from .cycle.cycle import Cycle
from .data.data_node import DataNode
from .exceptions import exceptions
from .job.job import Job
from .job.status import Status
from .pipeline.pipeline import Pipeline
from .scenario.scenario import Scenario
from .taipy import (
    cancel_job,
    clean_all_entities,
    clean_all_entities_by_version,
    compare_scenarios,
    create_pipeline,
    create_scenario,
    delete,
    delete_job,
    delete_jobs,
    export_scenario,
    get,
    get_cycles,
    get_data_nodes,
    get_jobs,
    get_latest_job,
    get_parents,
    get_pipelines,
    get_primary,
    get_primary_scenarios,
    get_scenarios,
    get_tasks,
    set,
    set_primary,
    submit,
    subscribe_pipeline,
    subscribe_scenario,
    tag,
    unsubscribe_pipeline,
    unsubscribe_scenario,
    untag,
)
from .task.task import Task

with open(f"{os.path.dirname(os.path.abspath(__file__))}{os.sep}version.json") as version_file:
    version = json.load(version_file)
    version_string = f'{version.get("major", 0)}.{version.get("minor", 0)}.{version.get("patch", 0)}'
    if vext := version.get("ext"):
        version_string = f"{version_string}.{vext}"

__version__ = version_string
