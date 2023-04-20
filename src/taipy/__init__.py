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

from importlib.util import find_spec

if find_spec("taipy"):
    if find_spec("taipy.config"):
        from taipy.config import Config, Frequency, Scope

    if find_spec("taipy.core"):
        from taipy.core._core import Core
        from taipy.core.cycle.cycle import Cycle
        from taipy.core.cycle.cycle_id import CycleId
        from taipy.core.data.data_node import DataNode
        from taipy.core.data.data_node_id import DataNodeId
        from taipy.core.job.job import Job
        from taipy.core.job.job_id import JobId
        from taipy.core.job.status import Status
        from taipy.core.pipeline.pipeline import Pipeline
        from taipy.core.pipeline.pipeline_id import PipelineId
        from taipy.core.scenario.scenario import Scenario
        from taipy.core.scenario.scenario_id import ScenarioId
        from taipy.core.taipy import (
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
            get_cycles_scenarios,
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
        from taipy.core.task.task import Task
        from taipy.core.task.task_id import TaskId

    if find_spec("taipy.gui"):
        from taipy.gui import Gui

        if find_spec("taipy.enterprise") and find_spec("taipy.enterprise.gui"):
            from taipy.enterprise.gui import _init_gui_enterprise

            _init_gui_enterprise(Gui)

    if find_spec("taipy.rest"):
        from taipy.rest import Rest

    if find_spec("taipy._run"):
        from taipy._run import _run as run
