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

import datetime
from unittest import mock

import taipy.core.taipy as tp
from taipy.core.common.alias import CycleId, JobId, PipelineId, ScenarioId, TaskId
from taipy.core.common.scope import Scope
from taipy.core.config.pipeline_config import PipelineConfig
from taipy.core.config.scenario_config import ScenarioConfig
from taipy.core.cycle._cycle_manager import _CycleManager
from taipy.core.data._data_manager import _DataManager
from taipy.core.job._job_manager import _JobManager
from taipy.core.job.job import Job
from taipy.core.pipeline._pipeline_manager import _PipelineManager
from taipy.core.scenario._scenario_manager import _ScenarioManager
from taipy.core.task._task_manager import _TaskManager

from taipy.core.config.config import Config


class TestTaipy:
    def test_set(self, scenario, cycle, pipeline, data_node, task):
        with mock.patch("taipy.core.data._data_manager._DataManager._set") as mck:
            tp.set(data_node, token="token")
            mck.assert_called_once_with(data_node, token="token")
        with mock.patch("taipy.core.task._task_manager._TaskManager._set") as mck:
            tp.set(task, token="token")
            mck.assert_called_once_with(task, token="token")
        with mock.patch("taipy.core.pipeline._pipeline_manager._PipelineManager._set") as mck:
            tp.set(pipeline, token="token")
            mck.assert_called_once_with(pipeline, token="token")
        with mock.patch("taipy.core.scenario._scenario_manager._ScenarioManager._set") as mck:
            tp.set(scenario, token="token")
            mck.assert_called_once_with(scenario, token="token")
        with mock.patch("taipy.core.cycle._cycle_manager._CycleManager._set") as mck:
            tp.set(cycle, token="token")
            mck.assert_called_once_with(cycle, token="token")

    def test_submit(self, scenario, pipeline, task):
        with mock.patch("taipy.core.scenario._scenario_manager._ScenarioManager._submit") as mck:
            tp.submit(scenario, token="token")
            mck.assert_called_once_with(scenario, force=False, token="token")
        with mock.patch("taipy.core.pipeline._pipeline_manager._PipelineManager._submit") as mck:
            tp.submit(pipeline, token="token")
            mck.assert_called_once_with(pipeline, force=False, token="token")
        with mock.patch("taipy.core.task._task_manager._TaskManager._submit") as mck:
            tp.submit(task, token="token")
            mck.assert_called_once_with(task, force=False, token="token")
        with mock.patch("taipy.core.scenario._scenario_manager._ScenarioManager._submit") as mck:
            tp.submit(scenario, False, token="token")
            mck.assert_called_once_with(scenario, force=False, token="token")
        with mock.patch("taipy.core.pipeline._pipeline_manager._PipelineManager._submit") as mck:
            tp.submit(pipeline, False, token="token")
            mck.assert_called_once_with(pipeline, force=False, token="token")
        with mock.patch("taipy.core.task._task_manager._TaskManager._submit") as mck:
            tp.submit(task, False, token="token")
            mck.assert_called_once_with(task, force=False, token="token")
        with mock.patch("taipy.core.scenario._scenario_manager._ScenarioManager._submit") as mck:
            tp.submit(scenario, True, token="token")
            mck.assert_called_once_with(scenario, force=True, token="token")
        with mock.patch("taipy.core.pipeline._pipeline_manager._PipelineManager._submit") as mck:
            tp.submit(pipeline, True, token="token")
            mck.assert_called_once_with(pipeline, force=True, token="token")
        with mock.patch("taipy.core.task._task_manager._TaskManager._submit") as mck:
            tp.submit(task, True, token="token")
            mck.assert_called_once_with(task, force=True, token="token")

    def test_get_tasks(self):
        with mock.patch("taipy.core.task._task_manager._TaskManager._get_all") as mck:
            tp.get_tasks(token="token")
            mck.assert_called_once_with(token="token")

    def test_get_task(self, task):
        with mock.patch("taipy.core.task._task_manager._TaskManager._get") as mck:
            task_id = TaskId("TASK_id")
            tp.get(task_id, token="token")
            mck.assert_called_once_with(task_id, token="token")

    def test_delete_scenario(self):
        with mock.patch("taipy.core.scenario._scenario_manager._ScenarioManager._hard_delete") as mck:
            scenario_id = ScenarioId("SCENARIO_id")
            tp.delete(scenario_id, token="token")
            mck.assert_called_once_with(scenario_id, token="token")

    def test_delete(self):
        with mock.patch("taipy.core.cycle._cycle_manager._CycleManager._hard_delete") as mck:
            cycle_id = CycleId("CYCLE_id")
            tp.delete(cycle_id, token="token")
            mck.assert_called_once_with(cycle_id, token="token")

    def test_get_scenarios(self, cycle):
        with mock.patch("taipy.core.scenario._scenario_manager._ScenarioManager._get_all") as mck:
            tp.get_scenarios(token="token")
            mck.assert_called_once_with(token="token")
        with mock.patch("taipy.core.scenario._scenario_manager._ScenarioManager._get_all_by_cycle") as mck:
            tp.get_scenarios(cycle, token="token")
            mck.assert_called_once_with(cycle, token="token")
        with mock.patch("taipy.core.scenario._scenario_manager._ScenarioManager._get_all_by_tag") as mck:
            tp.get_scenarios(tag="tag", token="token")
            mck.assert_called_once_with("tag", token="token")

    def test_get_scenario(self, scenario):
        with mock.patch("taipy.core.scenario._scenario_manager._ScenarioManager._get") as mck:
            scenario_id = ScenarioId("SCENARIO_id")
            tp.get(scenario_id, token="token")
            mck.assert_called_once_with(scenario_id, token="token")

    def test_get_primary(self, cycle):
        with mock.patch("taipy.core.scenario._scenario_manager._ScenarioManager._get_primary") as mck:
            tp.get_primary(cycle, token="token")
            mck.assert_called_once_with(cycle, token="token")

    def test_get_primary_scenarios(self):
        with mock.patch("taipy.core.scenario._scenario_manager._ScenarioManager._get_primary_scenarios") as mck:
            tp.get_primary_scenarios(token="token")
            mck.assert_called_once_with(token="token")

    def test_set_primary(self, scenario):
        with mock.patch("taipy.core.scenario._scenario_manager._ScenarioManager._set_primary") as mck:
            tp.set_primary(scenario, token="token")
            mck.assert_called_once_with(scenario, token="token")

    def test_tag_and_untag(self, scenario):
        with mock.patch("taipy.core.scenario._scenario_manager._ScenarioManager._tag") as mck:
            tp.tag(scenario, "tag", token="token")
            mck.assert_called_once_with(scenario, "tag", token="token")
        with mock.patch("taipy.core.scenario._scenario_manager._ScenarioManager._untag") as mck:
            tp.untag(scenario, "tag", token="token")
            mck.assert_called_once_with(scenario, "tag", token="token")

    def test_compare_scenarios(self, scenario):
        with mock.patch("taipy.core.scenario._scenario_manager._ScenarioManager._compare") as mck:
            tp.compare_scenarios(scenario, scenario, data_node_config_id="dn", token="token")
            mck.assert_called_once_with(scenario, scenario, data_node_config_id="dn", token="token")

    def test_subscribe_scenario(self, scenario):
        with mock.patch("taipy.core.scenario._scenario_manager._ScenarioManager._subscribe") as mck:
            tp.subscribe_scenario(print, token="token")
            mck.assert_called_once_with(print, None, token="token")
        with mock.patch("taipy.core.scenario._scenario_manager._ScenarioManager._subscribe") as mck:
            tp.subscribe_scenario(print, scenario=scenario, token="token")
            mck.assert_called_once_with(print, scenario, token="token")

    def test_unsubscribe_scenario(self, scenario):
        with mock.patch("taipy.core.scenario._scenario_manager._ScenarioManager._unsubscribe") as mck:
            tp.unsubscribe_scenario(print, token="token")
            mck.assert_called_once_with(print, None, token="token")
        with mock.patch("taipy.core.scenario._scenario_manager._ScenarioManager._unsubscribe") as mck:
            tp.unsubscribe_scenario(print, scenario=scenario, token="token")
            mck.assert_called_once_with(print, scenario, token="token")

    def test_subscribe_pipeline(self, pipeline):
        with mock.patch("taipy.core.pipeline._pipeline_manager._PipelineManager._subscribe") as mck:
            tp.subscribe_pipeline(print, token="token")
            mck.assert_called_once_with(print, None, token="token")
        with mock.patch("taipy.core.pipeline._pipeline_manager._PipelineManager._subscribe") as mck:
            tp.subscribe_pipeline(print, pipeline=pipeline, token="token")
            mck.assert_called_once_with(print, pipeline, token="token")

    def test_unsubscribe_pipeline(self, pipeline):
        with mock.patch("taipy.core.pipeline._pipeline_manager._PipelineManager._unsubscribe") as mck:
            tp.unsubscribe_pipeline(print, token="token")
            mck.assert_called_once_with(print, None, token="token")
        with mock.patch("taipy.core.pipeline._pipeline_manager._PipelineManager._unsubscribe") as mck:
            tp.unsubscribe_pipeline(print, pipeline=pipeline, token="token")
            mck.assert_called_once_with(print, pipeline, token="token")

    def test_delete_pipeline(self):
        with mock.patch("taipy.core.pipeline._pipeline_manager._PipelineManager._hard_delete") as mck:
            pipeline_id = PipelineId("PIPELINE_id")
            tp.delete(pipeline_id, token="token")
            mck.assert_called_once_with(pipeline_id, token="token")

    def test_get_pipeline(self, pipeline):
        with mock.patch("taipy.core.pipeline._pipeline_manager._PipelineManager._get") as mck:
            pipeline_id = PipelineId("PIPELINE_id")
            tp.get(pipeline_id, token="token")
            mck.assert_called_once_with(pipeline_id, token="token")

    def test_get_pipelines(self):
        with mock.patch("taipy.core.pipeline._pipeline_manager._PipelineManager._get_all") as mck:
            tp.get_pipelines(token="token")
            mck.assert_called_once_with(token="token")

    def test_get_job(self):
        with mock.patch("taipy.core.job._job_manager._JobManager._get") as mck:
            job_id = JobId("JOB_id")
            tp.get(job_id, token="token")
            mck.assert_called_once_with(job_id, token="token")

    def test_get_jobs(self):
        with mock.patch("taipy.core.job._job_manager._JobManager._get_all") as mck:
            tp.get_jobs(token="token")
            mck.assert_called_once_with(token="token")

    def test_delete_job(self, task):
        with mock.patch("taipy.core.job._job_manager._JobManager._delete") as mck:
            job = Job(JobId("job_id"), task)
            tp.delete_job(job, token="token")
            mck.assert_called_once_with(job, False, token="token")
        with mock.patch("taipy.core.job._job_manager._JobManager._delete") as mck:
            job = Job(JobId("job_id"), task)
            tp.delete_job(job, False, token="token")
            mck.assert_called_once_with(job, False, token="token")
        with mock.patch("taipy.core.job._job_manager._JobManager._delete") as mck:
            job = Job(JobId("job_id"), task)
            tp.delete_job(job, True, token="token")
            mck.assert_called_once_with(job, True, token="token")

    def test_delete_jobs(self):
        with mock.patch("taipy.core.job._job_manager._JobManager._delete_all") as mck:
            tp.delete_jobs(token="token")
            mck.assert_called_once_with(token="token")

    def test_get_latest_job(self, task):
        with mock.patch("taipy.core.job._job_manager._JobManager._get_latest") as mck:
            tp.get_latest_job(task, token="token")
            mck.assert_called_once_with(task, token="token")

    def test_get_data_node(self, data_node):
        with mock.patch("taipy.core.data._data_manager._DataManager._get") as mck:
            tp.get(data_node.id, token="token")
            mck.assert_called_once_with(data_node.id, token="token")

    def test_get_data_nodes(self):
        with mock.patch("taipy.core.data._data_manager._DataManager._get_all") as mck:
            tp.get_data_nodes(token="token")
            mck.assert_called_once_with(token="token")

    def test_get_cycles(self):
        with mock.patch("taipy.core.cycle._cycle_manager._CycleManager._get_all") as mck:
            tp.get_cycles(token="token")
            mck.assert_called_once_with(token="token")

    def test_create_scenario(self, scenario):
        scenario_config = ScenarioConfig("scenario_config")
        with mock.patch("taipy.core.scenario._scenario_manager._ScenarioManager._create") as mck:
            tp.create_scenario(scenario_config, token="token")
            mck.assert_called_once_with(scenario_config, None, None, token="token")
        with mock.patch("taipy.core.scenario._scenario_manager._ScenarioManager._create") as mck:
            tp.create_scenario(scenario_config, datetime.datetime(2022, 2, 5), token="token")
            mck.assert_called_once_with(scenario_config, datetime.datetime(2022, 2, 5), None, token="token")
        with mock.patch("taipy.core.scenario._scenario_manager._ScenarioManager._create") as mck:
            tp.create_scenario(scenario_config, datetime.datetime(2022, 2, 5), "displayable_name", token="token")
            mck.assert_called_once_with(
                scenario_config, datetime.datetime(2022, 2, 5), "displayable_name", token="token"
            )

    def test_create_pipeline(self):
        pipeline_config = PipelineConfig("pipeline_config")
        with mock.patch("taipy.core.pipeline._pipeline_manager._PipelineManager._get_or_create") as mck:
            tp.create_pipeline(pipeline_config, token="token")
            mck.assert_called_once_with(pipeline_config, token="token")

    def test_clean_all_entities(self, cycle):
        data_node_1_config = Config.configure_data_node(id="d1", storage_type="in_memory", scope=Scope.SCENARIO)
        data_node_2_config = Config.configure_data_node(
            id="d2", storage_type="pickle", default_data="abc", scope=Scope.SCENARIO
        )
        task_config = Config.configure_task(
            "my_task", print, data_node_1_config, data_node_2_config, scope=Scope.SCENARIO
        )
        pipeline_config = Config.configure_pipeline("my_pipeline", task_config)
        scenario_config = Config.configure_scenario("my_scenario", pipeline_config)
        _CycleManager._set(cycle)

        scenario = _ScenarioManager._create(scenario_config)
        _ScenarioManager._submit(scenario)

        # Initial assertion
        assert len(_DataManager._get_all()) == 2
        assert len(_TaskManager._get_all()) == 1
        assert len(_PipelineManager._get_all()) == 1
        assert len(_ScenarioManager._get_all()) == 1
        assert len(_CycleManager._get_all()) == 1
        assert len(_JobManager._get_all()) == 1

        # Test with clean entities disabled
        Config.configure_global_app(clean_entities_enabled=False)
        success = tp.clean_all_entities()
        # Everything should be the same after clean_all_entities since clean_entities_enabled is False
        assert len(_DataManager._get_all()) == 2
        assert len(_TaskManager._get_all()) == 1
        assert len(_PipelineManager._get_all()) == 1
        assert len(_ScenarioManager._get_all()) == 1
        assert len(_CycleManager._get_all()) == 1
        assert len(_JobManager._get_all()) == 1
        assert not success

        # Test with clean entities enabled
        Config.configure_global_app(clean_entities_enabled=True)
        success = tp.clean_all_entities()
        # File should not exist after clean_all_entities since clean_entities_enabled is True
        assert len(_DataManager._get_all()) == 0
        assert len(_TaskManager._get_all()) == 0
        assert len(_PipelineManager._get_all()) == 0
        assert len(_ScenarioManager._get_all()) == 0
        assert len(_CycleManager._get_all()) == 0
        assert len(_JobManager._get_all()) == 0
        assert success
