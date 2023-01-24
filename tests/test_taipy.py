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

import datetime
import os
import pathlib
import shutil
from unittest import mock

import pytest

import src.taipy.core.taipy as tp
from src.taipy.core import Core
from src.taipy.core._scheduler._scheduler_factory import _SchedulerFactory
from src.taipy.core._version._version_manager import _VersionManager
from src.taipy.core.common.alias import CycleId, JobId, PipelineId, ScenarioId, TaskId
from src.taipy.core.config.job_config import JobConfig
from src.taipy.core.config.pipeline_config import PipelineConfig
from src.taipy.core.config.scenario_config import ScenarioConfig
from src.taipy.core.cycle._cycle_manager import _CycleManager
from src.taipy.core.data._data_manager import _DataManager
from src.taipy.core.exceptions.exceptions import InvalidExportPath
from src.taipy.core.job._job_manager import _JobManager
from src.taipy.core.job.job import Job
from src.taipy.core.pipeline._pipeline_manager import _PipelineManager
from src.taipy.core.scenario._scenario_manager import _ScenarioManager
from src.taipy.core.task._task_manager import _TaskManager
from taipy.config.common.frequency import Frequency
from taipy.config.common.scope import Scope
from taipy.config.config import Config
from taipy.config.exceptions.exceptions import ConfigurationUpdateBlocked


class TestTaipy:
    def test_set(self, scenario, cycle, pipeline, data_node, task):
        with mock.patch("src.taipy.core.data._data_manager._DataManager._set") as mck:
            tp.set(data_node)
            mck.assert_called_once_with(data_node)
        with mock.patch("src.taipy.core.task._task_manager._TaskManager._set") as mck:
            tp.set(task)
            mck.assert_called_once_with(task)
        with mock.patch("src.taipy.core.pipeline._pipeline_manager._PipelineManager._set") as mck:
            tp.set(pipeline)
            mck.assert_called_once_with(pipeline)
        with mock.patch("src.taipy.core.scenario._scenario_manager._ScenarioManager._set") as mck:
            tp.set(scenario)
            mck.assert_called_once_with(scenario)
        with mock.patch("src.taipy.core.cycle._cycle_manager._CycleManager._set") as mck:
            tp.set(cycle)
            mck.assert_called_once_with(cycle)

    def test_submit(self, scenario, pipeline, task):
        with mock.patch("src.taipy.core.scenario._scenario_manager._ScenarioManager._submit") as mck:
            tp.submit(scenario)
            mck.assert_called_once_with(scenario, force=False, wait=False, timeout=None)
        with mock.patch("src.taipy.core.pipeline._pipeline_manager._PipelineManager._submit") as mck:
            tp.submit(pipeline)
            mck.assert_called_once_with(pipeline, force=False, wait=False, timeout=None)
        with mock.patch("src.taipy.core.task._task_manager._TaskManager._submit") as mck:
            tp.submit(task)
            mck.assert_called_once_with(task, force=False, wait=False, timeout=None)
        with mock.patch("src.taipy.core.scenario._scenario_manager._ScenarioManager._submit") as mck:
            tp.submit(scenario, False, False, None)
            mck.assert_called_once_with(scenario, force=False, wait=False, timeout=None)
        with mock.patch("src.taipy.core.pipeline._pipeline_manager._PipelineManager._submit") as mck:
            tp.submit(pipeline, False, False, None)
            mck.assert_called_once_with(pipeline, force=False, wait=False, timeout=None)
        with mock.patch("src.taipy.core.task._task_manager._TaskManager._submit") as mck:
            tp.submit(task, False, False, None)
            mck.assert_called_once_with(task, force=False, wait=False, timeout=None)
        with mock.patch("src.taipy.core.scenario._scenario_manager._ScenarioManager._submit") as mck:
            tp.submit(scenario, True, True, 60)
            mck.assert_called_once_with(scenario, force=True, wait=True, timeout=60)
        with mock.patch("src.taipy.core.pipeline._pipeline_manager._PipelineManager._submit") as mck:
            tp.submit(pipeline, True, True, 60)
            mck.assert_called_once_with(pipeline, force=True, wait=True, timeout=60)
        with mock.patch("src.taipy.core.task._task_manager._TaskManager._submit") as mck:
            tp.submit(task, True, True, 60)
            mck.assert_called_once_with(task, force=True, wait=True, timeout=60)

    def test_warning_no_core_service_running(self, scenario):
        _SchedulerFactory._remove_dispatcher()

        with pytest.warns(ResourceWarning) as warning:
            with mock.patch("src.taipy.core.scenario._scenario_manager._ScenarioManager._submit"):
                tp.submit(scenario)

        assert len(warning) == 1
        assert warning[0].message.args[0] == "The Core service is NOT running"

    def test_get_tasks(self):
        with mock.patch("src.taipy.core.task._task_manager._TaskManager._get_all") as mck:
            tp.get_tasks()
            mck.assert_called_once_with()

    def test_get_task(self, task):
        with mock.patch("src.taipy.core.task._task_manager._TaskManager._get") as mck:
            task_id = TaskId("TASK_id")
            tp.get(task_id)
            mck.assert_called_once_with(task_id)

    def test_delete_scenario(self):
        with mock.patch("src.taipy.core.scenario._scenario_manager._ScenarioManager._hard_delete") as mck:
            scenario_id = ScenarioId("SCENARIO_id")
            tp.delete(scenario_id)
            mck.assert_called_once_with(scenario_id)

    def test_delete(self):
        with mock.patch("src.taipy.core.cycle._cycle_manager._CycleManager._hard_delete") as mck:
            cycle_id = CycleId("CYCLE_id")
            tp.delete(cycle_id)
            mck.assert_called_once_with(cycle_id)

    def test_get_scenarios(self, cycle):
        with mock.patch("src.taipy.core.scenario._scenario_manager._ScenarioManager._get_all") as mck:
            tp.get_scenarios()
            mck.assert_called_once_with()
        with mock.patch("src.taipy.core.scenario._scenario_manager._ScenarioManager._get_all_by_cycle") as mck:
            tp.get_scenarios(cycle)
            mck.assert_called_once_with(cycle)
        with mock.patch("src.taipy.core.scenario._scenario_manager._ScenarioManager._get_all_by_tag") as mck:
            tp.get_scenarios(tag="tag")
            mck.assert_called_once_with("tag")

    def test_get_scenario(self, scenario):
        with mock.patch("src.taipy.core.scenario._scenario_manager._ScenarioManager._get") as mck:
            scenario_id = ScenarioId("SCENARIO_id")
            tp.get(scenario_id)
            mck.assert_called_once_with(scenario_id)

    def test_get_primary(self, cycle):
        with mock.patch("src.taipy.core.scenario._scenario_manager._ScenarioManager._get_primary") as mck:
            tp.get_primary(cycle)
            mck.assert_called_once_with(cycle)

    def test_get_primary_scenarios(self):
        with mock.patch("src.taipy.core.scenario._scenario_manager._ScenarioManager._get_primary_scenarios") as mck:
            tp.get_primary_scenarios()
            mck.assert_called_once_with()

    def test_set_primary(self, scenario):
        with mock.patch("src.taipy.core.scenario._scenario_manager._ScenarioManager._set_primary") as mck:
            tp.set_primary(scenario)
            mck.assert_called_once_with(scenario)

    def test_tag_and_untag(self, scenario):
        with mock.patch("src.taipy.core.scenario._scenario_manager._ScenarioManager._tag") as mck:
            tp.tag(scenario, "tag")
            mck.assert_called_once_with(scenario, "tag")
        with mock.patch("src.taipy.core.scenario._scenario_manager._ScenarioManager._untag") as mck:
            tp.untag(scenario, "tag")
            mck.assert_called_once_with(scenario, "tag")

    def test_compare_scenarios(self, scenario):
        with mock.patch("src.taipy.core.scenario._scenario_manager._ScenarioManager._compare") as mck:
            tp.compare_scenarios(scenario, scenario, data_node_config_id="dn")
            mck.assert_called_once_with(scenario, scenario, data_node_config_id="dn")

    def test_subscribe_scenario(self, scenario):
        with mock.patch("src.taipy.core.scenario._scenario_manager._ScenarioManager._subscribe") as mck:
            tp.subscribe_scenario(print)
            mck.assert_called_once_with(print, [], None)
        with mock.patch("src.taipy.core.scenario._scenario_manager._ScenarioManager._subscribe") as mck:
            tp.subscribe_scenario(print, scenario=scenario)
            mck.assert_called_once_with(print, [], scenario)

    def test_unsubscribe_scenario(self, scenario):
        with mock.patch("src.taipy.core.scenario._scenario_manager._ScenarioManager._unsubscribe") as mck:
            tp.unsubscribe_scenario(print)
            mck.assert_called_once_with(print, None, None)
        with mock.patch("src.taipy.core.scenario._scenario_manager._ScenarioManager._unsubscribe") as mck:
            tp.unsubscribe_scenario(print, scenario=scenario)
            mck.assert_called_once_with(print, None, scenario)

    def test_subscribe_pipeline(self, pipeline):
        with mock.patch("src.taipy.core.pipeline._pipeline_manager._PipelineManager._subscribe") as mck:
            tp.subscribe_pipeline(print)
            mck.assert_called_once_with(print, None, None)
        with mock.patch("src.taipy.core.pipeline._pipeline_manager._PipelineManager._subscribe") as mck:
            tp.subscribe_pipeline(print, pipeline=pipeline)
            mck.assert_called_once_with(print, None, pipeline)

    def test_unsubscribe_pipeline(self, pipeline):
        with mock.patch("src.taipy.core.pipeline._pipeline_manager._PipelineManager._unsubscribe") as mck:
            tp.unsubscribe_pipeline(callback=print)
            mck.assert_called_once_with(print, None, None)
        with mock.patch("src.taipy.core.pipeline._pipeline_manager._PipelineManager._unsubscribe") as mck:
            tp.unsubscribe_pipeline(callback=print, pipeline=pipeline)
            mck.assert_called_once_with(print, None, pipeline)

    def test_delete_pipeline(self):
        with mock.patch("src.taipy.core.pipeline._pipeline_manager._PipelineManager._hard_delete") as mck:
            pipeline_id = PipelineId("PIPELINE_id")
            tp.delete(pipeline_id)
            mck.assert_called_once_with(pipeline_id)

    def test_get_pipeline(self, pipeline):
        with mock.patch("src.taipy.core.pipeline._pipeline_manager._PipelineManager._get") as mck:
            pipeline_id = PipelineId("PIPELINE_id")
            tp.get(pipeline_id)
            mck.assert_called_once_with(pipeline_id)

    def test_get_pipelines(self):
        with mock.patch("src.taipy.core.pipeline._pipeline_manager._PipelineManager._get_all") as mck:
            tp.get_pipelines()
            mck.assert_called_once_with()

    def test_get_job(self):
        with mock.patch("src.taipy.core.job._job_manager._JobManager._get") as mck:
            job_id = JobId("JOB_id")
            tp.get(job_id)
            mck.assert_called_once_with(job_id)

    def test_get_jobs(self):
        with mock.patch("src.taipy.core.job._job_manager._JobManager._get_all") as mck:
            tp.get_jobs()
            mck.assert_called_once_with()

    def test_delete_job(self, task):
        with mock.patch("src.taipy.core.job._job_manager._JobManager._delete") as mck:
            job = Job(JobId("job_id"), task, "submit_id")
            tp.delete_job(job)
            mck.assert_called_once_with(job, False)
        with mock.patch("src.taipy.core.job._job_manager._JobManager._delete") as mck:
            job = Job(JobId("job_id"), task, "submit_id")
            tp.delete_job(job, False)
            mck.assert_called_once_with(job, False)
        with mock.patch("src.taipy.core.job._job_manager._JobManager._delete") as mck:
            job = Job(JobId("job_id"), task, "submit_id")
            tp.delete_job(job, True)
            mck.assert_called_once_with(job, True)

    def test_delete_jobs(self):
        with mock.patch("src.taipy.core.job._job_manager._JobManager._delete_all") as mck:
            tp.delete_jobs()
            mck.assert_called_once_with()

    def test_get_latest_job(self, task):
        with mock.patch("src.taipy.core.job._job_manager._JobManager._get_latest") as mck:
            tp.get_latest_job(task)
            mck.assert_called_once_with(task)

    def test_cancel_job(self):
        with mock.patch("src.taipy.core.job._job_manager._JobManager._cancel") as mck:
            tp.cancel_job("job_id")
            mck.assert_called_once_with("job_id")

    def test_block_config_when_core_is_running_in_development_mode(self):
        Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)

        input_cfg_1 = Config.configure_data_node(id="i1", storage_type="pickle", default_data=1, scope=Scope.PIPELINE)
        output_cfg_1 = Config.configure_data_node(id="o1", storage_type="pickle", scope=Scope.PIPELINE)
        task_cfg_1 = Config.configure_task("t1", print, input_cfg_1, output_cfg_1)
        pipeline_cfg_1 = Config.configure_pipeline("p1", task_cfg_1)
        scenario_cfg_1 = Config.configure_scenario("s1", pipeline_cfg_1, Frequency.DAILY)

        Core().run()

        scenario_1 = tp.create_scenario(scenario_cfg_1)
        tp.submit(scenario_1)

        with pytest.raises(ConfigurationUpdateBlocked):
            Config.configure_scenario("block_scenario", pipeline_cfg_1)

    def test_block_config_when_core_is_running_in_standalone_mode(self):
        Config.configure_job_executions(mode=JobConfig._STANDALONE_MODE)

        input_cfg_1 = Config.configure_data_node(id="i1", storage_type="pickle", default_data=1, scope=Scope.PIPELINE)
        output_cfg_1 = Config.configure_data_node(id="o1", storage_type="pickle", scope=Scope.PIPELINE)
        task_cfg_1 = Config.configure_task("t1", print, input_cfg_1, output_cfg_1)
        pipeline_cfg_1 = Config.configure_pipeline("p1", task_cfg_1)
        scenario_cfg_1 = Config.configure_scenario("s1", pipeline_cfg_1, Frequency.DAILY)

        Core().run()

        scenario_1 = tp.create_scenario(scenario_cfg_1)
        tp.submit(scenario_1, wait=True)

        with pytest.raises(ConfigurationUpdateBlocked):
            Config.configure_scenario("block_scenario", pipeline_cfg_1)

    def test_get_data_node(self, data_node):
        with mock.patch("src.taipy.core.data._data_manager._DataManager._get") as mck:
            tp.get(data_node.id)
            mck.assert_called_once_with(data_node.id)

    def test_get_data_nodes(self):
        with mock.patch("src.taipy.core.data._data_manager._DataManager._get_all") as mck:
            tp.get_data_nodes()
            mck.assert_called_once_with()

    def test_get_cycles(self):
        with mock.patch("src.taipy.core.cycle._cycle_manager._CycleManager._get_all") as mck:
            tp.get_cycles()
            mck.assert_called_once_with()

    def test_create_scenario(self, scenario):
        scenario_config = ScenarioConfig("scenario_config")
        with mock.patch("src.taipy.core.scenario._scenario_manager._ScenarioManager._create") as mck:
            tp.create_scenario(scenario_config)
            mck.assert_called_once_with(scenario_config, None, None)
        with mock.patch("src.taipy.core.scenario._scenario_manager._ScenarioManager._create") as mck:
            tp.create_scenario(scenario_config, datetime.datetime(2022, 2, 5))
            mck.assert_called_once_with(scenario_config, datetime.datetime(2022, 2, 5), None)
        with mock.patch("src.taipy.core.scenario._scenario_manager._ScenarioManager._create") as mck:
            tp.create_scenario(scenario_config, datetime.datetime(2022, 2, 5), "displayable_name")
            mck.assert_called_once_with(scenario_config, datetime.datetime(2022, 2, 5), "displayable_name")

    def test_create_pipeline(self):
        pipeline_config = PipelineConfig("pipeline_config")
        with mock.patch("src.taipy.core.pipeline._pipeline_manager._PipelineManager._get_or_create") as mck:
            tp.create_pipeline(pipeline_config)
            mck.assert_called_once_with(pipeline_config)

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

        Core().run()
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
        assert len(_VersionManager._get_all()) == 1

        # Temporarily unblock config update to test config global app
        Config.unblock_update()

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
        assert len(_VersionManager._get_all()) == 1
        assert not success

        # Test with clean entities enabled
        Config.configure_global_app(clean_entities_enabled=True)
        success = tp.clean_all_entities()
        # File should not exist after clean_all_entities since clean_entities_enabled is True
        assert len(_VersionManager._get_all()) == 0
        assert len(_DataManager._get_all()) == 0
        assert len(_TaskManager._get_all()) == 0
        assert len(_PipelineManager._get_all()) == 0
        assert len(_ScenarioManager._get_all()) == 0
        assert len(_CycleManager._get_all()) == 0
        assert len(_JobManager._get_all()) == 0
        assert success

    def test_export_scenario_filesystem(self):
        shutil.rmtree("./tmp", ignore_errors=True)

        input_cfg_1 = Config.configure_data_node(id="i1", storage_type="pickle", default_data=1, scope=Scope.PIPELINE)
        output_cfg_1 = Config.configure_data_node(id="o1", storage_type="pickle", scope=Scope.PIPELINE)
        task_cfg_1 = Config.configure_task("t1", print, input_cfg_1, output_cfg_1)
        pipeline_cfg_1 = Config.configure_pipeline("p1", task_cfg_1)
        scenario_cfg_1 = Config.configure_scenario("s1", pipeline_cfg_1, Frequency.DAILY)

        input_cfg_2 = Config.configure_data_node(id="i2", storage_type="pickle", default_data=2, scope=Scope.SCENARIO)
        output_cfg_2 = Config.configure_data_node(id="o2", storage_type="pickle", scope=Scope.SCENARIO)
        task_cfg_2 = Config.configure_task("t2", print, input_cfg_2, output_cfg_2)
        pipeline_cfg_2 = Config.configure_pipeline("p2", task_cfg_2)
        scenario_cfg_2 = Config.configure_scenario("s2", pipeline_cfg_2, Frequency.DAILY)

        scenario_1 = tp.create_scenario(scenario_cfg_1)
        job_1 = tp.submit(scenario_1)
        job_1 = job_1[scenario_1.p1.id][0]

        # Export scenario 1
        tp.export_scenario(scenario_1.id, "./tmp/exp_scenario_1")
        assert sorted(os.listdir("./tmp/exp_scenario_1/data_nodes")) == sorted(
            [f"{scenario_1.i1.id}.json", f"{scenario_1.o1.id}.json"]
        )
        assert sorted(os.listdir("./tmp/exp_scenario_1/tasks")) == sorted([f"{scenario_1.t1.id}.json"])
        assert sorted(os.listdir("./tmp/exp_scenario_1/pipelines")) == sorted([f"{scenario_1.p1.id}.json"])
        assert sorted(os.listdir("./tmp/exp_scenario_1/scenarios")) == sorted([f"{scenario_1.id}.json"])
        assert sorted(os.listdir("./tmp/exp_scenario_1/jobs")) == sorted([f"{job_1.id}.json"])
        assert sorted(os.listdir("./tmp/exp_scenario_1/cycles")) == sorted([f"{scenario_1.cycle.id}.json"])

        scenario_2 = tp.create_scenario(scenario_cfg_2)
        job_2 = tp.submit(scenario_2)
        job_2 = job_2[scenario_2.p2.id][0]

        # Export scenario 2
        scenario_2.export(pathlib.Path.cwd() / "./tmp/exp_scenario_2")
        assert sorted(os.listdir("./tmp/exp_scenario_2/data_nodes")) == sorted(
            [f"{scenario_2.i2.id}.json", f"{scenario_2.o2.id}.json"]
        )
        assert sorted(os.listdir("./tmp/exp_scenario_2/tasks")) == sorted([f"{scenario_2.t2.id}.json"])
        assert sorted(os.listdir("./tmp/exp_scenario_2/pipelines")) == sorted([f"{scenario_2.p2.id}.json"])
        assert sorted(os.listdir("./tmp/exp_scenario_2/scenarios")) == sorted([f"{scenario_2.id}.json"])
        assert sorted(os.listdir("./tmp/exp_scenario_2/jobs")) == sorted([f"{job_2.id}.json"])
        assert sorted(os.listdir("./tmp/exp_scenario_2/cycles")) == sorted([f"{scenario_2.cycle.id}.json"])

        # Export scenario 2 into the folder containing scenario 1 files
        tp.export_scenario(scenario_2.id, "./tmp/exp_scenario_1")
        # Should have the files as scenario 1 only
        assert sorted(os.listdir("./tmp/exp_scenario_1/tasks")) == sorted([f"{scenario_2.t2.id}.json"])
        assert sorted(os.listdir("./tmp/exp_scenario_1/pipelines")) == sorted([f"{scenario_2.p2.id}.json"])
        assert sorted(os.listdir("./tmp/exp_scenario_1/scenarios")) == sorted([f"{scenario_2.id}.json"])
        assert sorted(os.listdir("./tmp/exp_scenario_1/jobs")) == sorted([f"{job_2.id}.json"])
        assert sorted(os.listdir("./tmp/exp_scenario_1/cycles")) == sorted([f"{scenario_2.cycle.id}.json"])

        with pytest.raises(InvalidExportPath):
            tp.export_scenario(scenario_2.id, Config.global_config.storage_folder)

        shutil.rmtree("./tmp", ignore_errors=True)

    def test_get_parents(self):
        def assert_result_parents_and_expected_parents(parents, expected_parents):
            for key, items in expected_parents.items():
                assert len(parents[key]) == len(expected_parents[key])
                parent_ids = [parent.id for parent in parents[key]]
                assert all([item.id in parent_ids for item in items])

        dn_config_1 = Config.configure_data_node(id="d1", storage_type="in_memory", scope=Scope.SCENARIO)
        dn_config_2 = Config.configure_data_node(id="d2", storage_type="in_memory", scope=Scope.SCENARIO)
        dn_config_3 = Config.configure_data_node(id="d3", storage_type="in_memory", scope=Scope.SCENARIO)
        task_config_1 = Config.configure_task("t1", print, dn_config_1, dn_config_2)
        task_config_2 = Config.configure_task("t2", print, dn_config_2, dn_config_3)
        pipeline_config_1 = Config.configure_pipeline("p1", task_config_1)
        pipeline_config_2 = Config.configure_pipeline("p2", [task_config_1, task_config_2])
        scenario_cfg_1 = Config.configure_scenario("s1", [pipeline_config_1, pipeline_config_2], Frequency.DAILY)

        scenario = tp.create_scenario(scenario_cfg_1)
        pipelines = scenario.pipelines
        tasks = {}
        for pipeline in pipelines.values():
            tasks.update(pipeline.tasks)

        expected_parents = {
            "scenarios": {scenario},
            "pipelines": {pipelines["p1"], pipelines["p2"]},
            "tasks": {tasks["t1"]},
        }
        parents = tp.get_parents(scenario.pipelines["p1"].tasks["t1"].data_nodes["d1"])
        assert_result_parents_and_expected_parents(parents, expected_parents)

        expected_parents = {
            "scenarios": {scenario},
            "pipelines": {pipelines["p1"], pipelines["p2"]},
            "tasks": {tasks["t1"], tasks["t2"]},
        }
        parents = tp.get_parents(scenario.pipelines["p1"].tasks["t1"].data_nodes["d2"])
        assert_result_parents_and_expected_parents(parents, expected_parents)

        expected_parents = {"scenarios": {scenario}, "pipelines": {pipelines["p2"]}, "tasks": {tasks["t2"]}}
        parents = tp.get_parents(scenario.pipelines["p2"].tasks["t2"].data_nodes["d3"])
        assert_result_parents_and_expected_parents(parents, expected_parents)

        expected_parents = {"scenarios": {scenario}, "pipelines": {pipelines["p1"], pipelines["p2"]}}
        parents = tp.get_parents(scenario.pipelines["p2"].tasks["t1"])
        assert_result_parents_and_expected_parents(parents, expected_parents)

        expected_parents = {"scenarios": {scenario}, "pipelines": {pipelines["p2"]}}
        parents = tp.get_parents(scenario.pipelines["p2"].tasks["t2"])
        assert_result_parents_and_expected_parents(parents, expected_parents)

        expected_parents = {"scenarios": {scenario}}
        parents = tp.get_parents(scenario.pipelines["p1"])
        assert_result_parents_and_expected_parents(parents, expected_parents)

        expected_parents = {"scenarios": {scenario}}
        parents = tp.get_parents(scenario.pipelines["p2"])
        assert_result_parents_and_expected_parents(parents, expected_parents)

        expected_parents = {}
        parents = tp.get_parents(scenario)
        assert_result_parents_and_expected_parents(parents, expected_parents)

        expected_parents = {}
        parents = tp.get_parents(scenario.cycle)
        assert_result_parents_and_expected_parents(parents, expected_parents)
