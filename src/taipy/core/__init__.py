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

from ._core import Core
from .common.alias import CycleId, DataNodeId, JobId, PipelineId, ScenarioId, TaskId
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

"""# Taipy Core.

The Taipy Core package is a Python library made to build powerful and customized data-driven back-end applications.
It provides the necessary tools to help Python developers transform their algorithms into a complete
back-end application.

!!! Note "Optional packages"

    There are Python packages that you can install in your environment to
    add functionality to Taipy Core:

    - [`pyodbc`](https://pypi.org/project/pyodbc/), [`pymysql`](https://pypi.org/project/PyMySQL/), [`psycopg2`](https://www.psycopg.org/): are used by data nodes configured using the predefined [`SQL data node config`](../../core/config/data-node-config.md#sql) with `mssql`, `mysql`, and `postgresql` engines, respectively.
    You can install these packages :
        - directly with the regular `pip install <package-name>` command with the `<package-name>` is `pyodbc`, `pymysql`, or `psycopg2`.
        - by installing Taipy Core with extra packages for specific SQL engine, using: `pip install taipy-core[<sql-engine>]` with the `<sql-engine>` is `mssql`, `mysql`, or `postgresql`.
        - or by installing complete Taipy with extra packages for specific SQL engine, using: `pip install taipy[<sql-engine>]` with the `<sql-engine>` is `mssql`, `mysql`, or `postgresql`.
"""
