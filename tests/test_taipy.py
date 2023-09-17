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
from src.taipy.core import (
    Core,
    Cycle,
    CycleId,
    DataNodeId,
    JobId,
    Scenario,
    ScenarioId,
    Sequence,
    SequenceId,
    Task,
    TaskId,
)
from src.taipy.core._orchestrator._orchestrator_factory import _OrchestratorFactory
from src.taipy.core._version._version_manager import _VersionManager
from src.taipy.core.config.data_node_config import DataNodeConfig
from src.taipy.core.config.job_config import JobConfig
from src.taipy.core.config.scenario_config import ScenarioConfig
from src.taipy.core.cycle._cycle_manager import _CycleManager
from src.taipy.core.data._data_manager import _DataManager
from src.taipy.core.data.pickle import PickleDataNode
from src.taipy.core.exceptions.exceptions import DataNodeConfigIsNotGlobal, InvalidExportPath
from src.taipy.core.job._job_manager import _JobManager
from src.taipy.core.job.job import Job
from src.taipy.core.scenario._scenario_manager import _ScenarioManager
from src.taipy.core.sequence._sequence_manager import _SequenceManager
from src.taipy.core.task._task_manager import _TaskManager
from taipy.config.common.frequency import Frequency
from taipy.config.common.scope import Scope
from taipy.config.config import Config
from taipy.config.exceptions.exceptions import ConfigurationUpdateBlocked


class TestTaipy:
    def test_set(self, scenario, cycle, sequence, data_node, task):
        with mock.patch("src.taipy.core.data._data_manager._DataManager._set") as mck:
            tp.set(data_node)
            mck.assert_called_once_with(data_node)
        with mock.patch("src.taipy.core.task._task_manager._TaskManager._set") as mck:
            tp.set(task)
            mck.assert_called_once_with(task)
        with mock.patch("src.taipy.core.sequence._sequence_manager._SequenceManager._set") as mck:
            tp.set(sequence)
            mck.assert_called_once_with(sequence)
        with mock.patch("src.taipy.core.scenario._scenario_manager._ScenarioManager._set") as mck:
            tp.set(scenario)
            mck.assert_called_once_with(scenario)
        with mock.patch("src.taipy.core.cycle._cycle_manager._CycleManager._set") as mck:
            tp.set(cycle)
            mck.assert_called_once_with(cycle)

    def test_is_editable_is_called(self, cycle, job, data_node):
        with mock.patch("src.taipy.core.cycle._cycle_manager._CycleManager._is_editable") as mck:
            cycle_id = CycleId("CYCLE_id")
            tp.is_editable(cycle_id)
            mck.assert_called_once_with(cycle_id)

        with mock.patch("src.taipy.core.cycle._cycle_manager._CycleManager._is_editable") as mck:
            tp.is_editable(cycle)
            mck.assert_called_once_with(cycle)

        with mock.patch("src.taipy.core.scenario._scenario_manager._ScenarioManager._is_editable") as mck:
            scenario_id = ScenarioId("SCENARIO_id")
            tp.is_editable(scenario_id)
            mck.assert_called_once_with(scenario_id)

        with mock.patch("src.taipy.core.scenario._scenario_manager._ScenarioManager._is_editable") as mck:
            scenario = Scenario("scenario_config_id", [], {})
            tp.is_editable(scenario)
            mck.assert_called_once_with(scenario)

        with mock.patch("src.taipy.core.sequence._sequence_manager._SequenceManager._is_editable") as mck:
            sequence_id = SequenceId("SEQUENCE_id")
            tp.is_editable(sequence_id)
            mck.assert_called_once_with(sequence_id)

        with mock.patch("src.taipy.core.sequence._sequence_manager._SequenceManager._is_editable") as mck:
            sequence = Sequence({}, [], "sequence_id")
            tp.is_editable(sequence)
            mck.assert_called_once_with(sequence)

        with mock.patch("src.taipy.core.task._task_manager._TaskManager._is_editable") as mck:
            task_id = TaskId("TASK_id")
            tp.is_editable(task_id)
            mck.assert_called_once_with(task_id)

        with mock.patch("src.taipy.core.task._task_manager._TaskManager._is_editable") as mck:
            task = Task("task_config_id", {}, print)
            tp.is_editable(task)
            mck.assert_called_once_with(task)

        with mock.patch("src.taipy.core.job._job_manager._JobManager._is_editable") as mck:
            job_id = JobId("JOB_id")
            tp.is_editable(job_id)
            mck.assert_called_once_with(job_id)

        with mock.patch("src.taipy.core.job._job_manager._JobManager._is_editable") as mck:
            tp.is_editable(job)
            mck.assert_called_once_with(job)

        with mock.patch("src.taipy.core.data._data_manager._DataManager._is_editable") as mck:
            dn_id = DataNodeId("DATANODE_id")
            tp.is_editable(dn_id)
            mck.assert_called_once_with(dn_id)

        with mock.patch("src.taipy.core.data._data_manager._DataManager._is_editable") as mck:
            tp.is_editable(data_node)
            mck.assert_called_once_with(data_node)

    def test_is_editable(self):
        current_date = datetime.datetime.now()

        cycle = Cycle(Frequency.DAILY, {}, current_date, current_date, current_date)
        scenario = Scenario("scenario_config_id", [], {}, sequences={"sequence": {}})

        task = Task("task_config_id", {}, print)
        job = Job("job_id", task, "submit_id", scenario.id)
        dn = PickleDataNode("data_node_config_id", Scope.SCENARIO)

        _CycleManager._set(cycle)
        _ScenarioManager._set(scenario)
        _TaskManager._set(task)
        _JobManager._set(job)
        _DataManager._set(dn)
        sequence = scenario.sequences["sequence"]

        assert tp.is_editable(scenario)
        assert tp.is_editable(sequence)
        assert tp.is_editable(task)
        assert tp.is_editable(cycle)
        assert tp.is_editable(job)
        assert tp.is_editable(dn)

    def test_is_readable_is_called(self, cycle, job, data_node):
        with mock.patch("src.taipy.core.cycle._cycle_manager._CycleManager._is_readable") as mck:
            cycle_id = CycleId("CYCLE_id")
            tp.is_readable(cycle_id)
            mck.assert_called_once_with(cycle_id)

        with mock.patch("src.taipy.core.cycle._cycle_manager._CycleManager._is_readable") as mck:
            tp.is_readable(cycle)
            mck.assert_called_once_with(cycle)

        with mock.patch("src.taipy.core.scenario._scenario_manager._ScenarioManager._is_readable") as mck:
            scenario_id = ScenarioId("SCENARIO_id")
            tp.is_readable(scenario_id)
            mck.assert_called_once_with(scenario_id)

        with mock.patch("src.taipy.core.scenario._scenario_manager._ScenarioManager._is_readable") as mck:
            scenario = Scenario("scenario_config_id", [], {})
            tp.is_readable(scenario)
            mck.assert_called_once_with(scenario)

        with mock.patch("src.taipy.core.sequence._sequence_manager._SequenceManager._is_readable") as mck:
            sequence_id = SequenceId("SEQUENCE_id")
            tp.is_readable(sequence_id)
            mck.assert_called_once_with(sequence_id)

        with mock.patch("src.taipy.core.sequence._sequence_manager._SequenceManager._is_readable") as mck:
            sequence = Sequence({}, [], "sequence_id")
            tp.is_readable(sequence)
            mck.assert_called_once_with(sequence)

        with mock.patch("src.taipy.core.task._task_manager._TaskManager._is_readable") as mck:
            task_id = TaskId("TASK_id")
            tp.is_readable(task_id)
            mck.assert_called_once_with(task_id)

        with mock.patch("src.taipy.core.task._task_manager._TaskManager._is_readable") as mck:
            task = Task("task_config_id", {}, print)
            tp.is_readable(task)
            mck.assert_called_once_with(task)

        with mock.patch("src.taipy.core.job._job_manager._JobManager._is_readable") as mck:
            job_id = JobId("JOB_id")
            tp.is_readable(job_id)
            mck.assert_called_once_with(job_id)

        with mock.patch("src.taipy.core.job._job_manager._JobManager._is_readable") as mck:
            tp.is_readable(job)
            mck.assert_called_once_with(job)

        with mock.patch("src.taipy.core.data._data_manager._DataManager._is_readable") as mck:
            dn_id = DataNodeId("DATANODE_id")
            tp.is_readable(dn_id)
            mck.assert_called_once_with(dn_id)

        with mock.patch("src.taipy.core.data._data_manager._DataManager._is_readable") as mck:
            tp.is_readable(data_node)
            mck.assert_called_once_with(data_node)

    def test_is_readable(self):
        current_date = datetime.datetime.now()

        cycle = Cycle(Frequency.DAILY, {}, current_date, current_date, current_date)
        scenario = Scenario("scenario_config_id", [], {}, sequences={"sequence": {}})

        task = Task("task_config_id", {}, print)
        job = Job("job_id", task, "submit_id", scenario.id)
        dn = PickleDataNode("data_node_config_id", Scope.SCENARIO)

        _CycleManager._set(cycle)
        _ScenarioManager._set(scenario)
        _TaskManager._set(task)
        _JobManager._set(job)
        _DataManager._set(dn)
        sequence = scenario.sequences["sequence"]

        assert tp.is_readable(scenario)
        assert tp.is_readable(sequence)
        assert tp.is_readable(task)
        assert tp.is_readable(cycle)
        assert tp.is_readable(job)
        assert tp.is_readable(dn)

    def test_is_submittable_is_called(self):
        with mock.patch("src.taipy.core.scenario._scenario_manager._ScenarioManager._is_submittable") as mck:
            scenario_id = ScenarioId("SCENARIO_id")
            tp.is_submittable(scenario_id)
            mck.assert_called_once_with(scenario_id)

        with mock.patch("src.taipy.core.scenario._scenario_manager._ScenarioManager._is_submittable") as mck:
            scenario = Scenario("scenario_config_id", [], {})
            tp.is_submittable(scenario)
            mck.assert_called_once_with(scenario)

        with mock.patch("src.taipy.core.sequence._sequence_manager._SequenceManager._is_submittable") as mck:
            sequence_id = SequenceId("SEQUENCE_id")
            tp.is_submittable(sequence_id)
            mck.assert_called_once_with(sequence_id)

        with mock.patch("src.taipy.core.sequence._sequence_manager._SequenceManager._is_submittable") as mck:
            sequence = Sequence({}, [], "sequence_id")
            tp.is_submittable(sequence)
            mck.assert_called_once_with(sequence)

        with mock.patch("src.taipy.core.task._task_manager._TaskManager._is_submittable") as mck:
            task_id = TaskId("TASK_id")
            tp.is_submittable(task_id)
            mck.assert_called_once_with(task_id)

        with mock.patch("src.taipy.core.task._task_manager._TaskManager._is_submittable") as mck:
            task = Task("task_config_id", {}, print)
            tp.is_submittable(task)
            mck.assert_called_once_with(task)

    def test_is_submittable(self):
        current_date = datetime.datetime.now()

        cycle = Cycle(Frequency.DAILY, {}, current_date, current_date, current_date)
        scenario = Scenario("scenario_config_id", [], {}, sequences={"sequence": {}})

        task = Task("task_config_id", {}, print)
        job = Job("job_id", task, "submit_id", scenario.id)
        dn = PickleDataNode("data_node_config_id", Scope.SCENARIO)

        _CycleManager._set(cycle)
        _ScenarioManager._set(scenario)
        _TaskManager._set(task)
        _JobManager._set(job)
        _DataManager._set(dn)
        sequence = scenario.sequences["sequence"]

        assert tp.is_submittable(scenario)
        assert tp.is_submittable(sequence)
        assert tp.is_submittable(task)
        assert not tp.is_submittable(cycle)
        assert not tp.is_submittable(job)
        assert not tp.is_submittable(dn)

    def test_submit(self, scenario, sequence, task):
        with mock.patch("src.taipy.core.scenario._scenario_manager._ScenarioManager._submit") as mck:
            tp.submit(scenario)
            mck.assert_called_once_with(scenario, force=False, wait=False, timeout=None)
        with mock.patch("src.taipy.core.sequence._sequence_manager._SequenceManager._submit") as mck:
            tp.submit(sequence)
            mck.assert_called_once_with(sequence, force=False, wait=False, timeout=None)
        with mock.patch("src.taipy.core.task._task_manager._TaskManager._submit") as mck:
            tp.submit(task)
            mck.assert_called_once_with(task, force=False, wait=False, timeout=None)
        with mock.patch("src.taipy.core.scenario._scenario_manager._ScenarioManager._submit") as mck:
            tp.submit(scenario, False, False, None)
            mck.assert_called_once_with(scenario, force=False, wait=False, timeout=None)
        with mock.patch("src.taipy.core.sequence._sequence_manager._SequenceManager._submit") as mck:
            tp.submit(sequence, False, False, None)
            mck.assert_called_once_with(sequence, force=False, wait=False, timeout=None)
        with mock.patch("src.taipy.core.task._task_manager._TaskManager._submit") as mck:
            tp.submit(task, False, False, None)
            mck.assert_called_once_with(task, force=False, wait=False, timeout=None)
        with mock.patch("src.taipy.core.scenario._scenario_manager._ScenarioManager._submit") as mck:
            tp.submit(scenario, True, True, 60)
            mck.assert_called_once_with(scenario, force=True, wait=True, timeout=60)
        with mock.patch("src.taipy.core.sequence._sequence_manager._SequenceManager._submit") as mck:
            tp.submit(sequence, True, True, 60)
            mck.assert_called_once_with(sequence, force=True, wait=True, timeout=60)
        with mock.patch("src.taipy.core.task._task_manager._TaskManager._submit") as mck:
            tp.submit(task, True, True, 60)
            mck.assert_called_once_with(task, force=True, wait=True, timeout=60)

    def test_warning_no_core_service_running(self, scenario):
        _OrchestratorFactory._remove_dispatcher()

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

    def test_task_exists(self):
        with mock.patch("src.taipy.core.task._task_manager._TaskManager._exists") as mck:
            task_id = TaskId("TASK_id")
            tp.exists(task_id)
            mck.assert_called_once_with(task_id)

    def test_is_deletable(self, task):
        with mock.patch("src.taipy.core.scenario._scenario_manager._ScenarioManager._is_deletable") as mck:
            scenario_id = ScenarioId("SCENARIO_id")
            tp.is_deletable(scenario_id)
            mck.assert_called_once_with(scenario_id)

        with mock.patch("src.taipy.core.scenario._scenario_manager._ScenarioManager._is_deletable") as mck:
            scenario = Scenario("config_id", [], {})
            tp.is_deletable(scenario)
            mck.assert_called_once_with(scenario)

        with mock.patch("src.taipy.core.job._job_manager._JobManager._is_deletable") as mck:
            job_id = JobId("JOB_job_id")
            tp.is_deletable(job_id)
            mck.assert_called_once_with(job_id)

        with mock.patch("src.taipy.core.job._job_manager._JobManager._is_deletable") as mck:
            job = Job("job_id", task, "submit_id", task.id)
            tp.is_deletable(job)
            mck.assert_called_once_with(job)

    def test_is_promotable(self):
        with mock.patch("src.taipy.core.scenario._scenario_manager._ScenarioManager._is_promotable_to_primary") as mck:
            scenario_id = ScenarioId("SCENARIO_id")
            tp.is_promotable(scenario_id)
            mck.assert_called_once_with(scenario_id)

        with mock.patch("src.taipy.core.scenario._scenario_manager._ScenarioManager._is_promotable_to_primary") as mck:
            scenario = Scenario("config_id", [], {})
            tp.is_promotable(scenario)
            mck.assert_called_once_with(scenario)

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

    def test_scenario_exists(self):
        with mock.patch("src.taipy.core.scenario._scenario_manager._ScenarioManager._exists") as mck:
            scenario_id = ScenarioId("SCENARIO_id")
            tp.exists(scenario_id)
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

    def test_subscribe_sequence(self, sequence):
        with mock.patch("src.taipy.core.sequence._sequence_manager._SequenceManager._subscribe") as mck:
            tp.subscribe_sequence(print)
            mck.assert_called_once_with(print, None, None)
        with mock.patch("src.taipy.core.sequence._sequence_manager._SequenceManager._subscribe") as mck:
            tp.subscribe_sequence(print, sequence=sequence)
            mck.assert_called_once_with(print, None, sequence)

    def test_unsubscribe_sequence(self, sequence):
        with mock.patch("src.taipy.core.sequence._sequence_manager._SequenceManager._unsubscribe") as mck:
            tp.unsubscribe_sequence(callback=print)
            mck.assert_called_once_with(print, None, None)
        with mock.patch("src.taipy.core.sequence._sequence_manager._SequenceManager._unsubscribe") as mck:
            tp.unsubscribe_sequence(callback=print, sequence=sequence)
            mck.assert_called_once_with(print, None, sequence)

    def test_delete_sequence(self):
        with mock.patch("src.taipy.core.sequence._sequence_manager._SequenceManager._hard_delete") as mck:
            sequence_id = SequenceId("SEQUENCE_id")
            tp.delete(sequence_id)
            mck.assert_called_once_with(sequence_id)

    def test_get_sequence(self, sequence):
        with mock.patch("src.taipy.core.sequence._sequence_manager._SequenceManager._get") as mck:
            sequence_id = SequenceId("SEQUENCE_id")
            tp.get(sequence_id)
            mck.assert_called_once_with(sequence_id)

    def test_get_sequences(self):
        with mock.patch("src.taipy.core.sequence._sequence_manager._SequenceManager._get_all") as mck:
            tp.get_sequences()
            mck.assert_called_once_with()

    def test_sequence_exists(self):
        with mock.patch("src.taipy.core.sequence._sequence_manager._SequenceManager._exists") as mck:
            sequence_id = SequenceId("SEQUENCE_id")
            tp.exists(sequence_id)
            mck.assert_called_once_with(sequence_id)

    def test_get_job(self):
        with mock.patch("src.taipy.core.job._job_manager._JobManager._get") as mck:
            job_id = JobId("JOB_id")
            tp.get(job_id)
            mck.assert_called_once_with(job_id)

    def test_get_jobs(self):
        with mock.patch("src.taipy.core.job._job_manager._JobManager._get_all") as mck:
            tp.get_jobs()
            mck.assert_called_once_with()

    def test_job_exists(self):
        with mock.patch("src.taipy.core.job._job_manager._JobManager._exists") as mck:
            job_id = JobId("JOB_id")
            tp.exists(job_id)
            mck.assert_called_once_with(job_id)

    def test_delete_job(self, task):
        with mock.patch("src.taipy.core.job._job_manager._JobManager._delete") as mck:
            job = Job(JobId("job_id"), task, "submit_id", "scenario_id")
            tp.delete_job(job)
            mck.assert_called_once_with(job, False)
        with mock.patch("src.taipy.core.job._job_manager._JobManager._delete") as mck:
            job = Job(JobId("job_id"), task, "submit_id", "scenario_id")
            tp.delete_job(job, False)
            mck.assert_called_once_with(job, False)
        with mock.patch("src.taipy.core.job._job_manager._JobManager._delete") as mck:
            job = Job(JobId("job_id"), task, "submit_id", "scenario_id")
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

        input_cfg_1 = Config.configure_data_node(id="i1", storage_type="pickle", default_data=1, scope=Scope.SCENARIO)
        output_cfg_1 = Config.configure_data_node(id="o1", storage_type="pickle", scope=Scope.SCENARIO)
        task_cfg_1 = Config.configure_task("t1", print, input_cfg_1, output_cfg_1)
        scenario_cfg_1 = Config.configure_scenario("s1", [task_cfg_1], [], Frequency.DAILY)

        Core().run()

        scenario_1 = tp.create_scenario(scenario_cfg_1)
        tp.submit(scenario_1)

        with pytest.raises(ConfigurationUpdateBlocked):
            Config.configure_scenario("block_scenario", set([task_cfg_1]))

    def test_block_config_when_core_is_running_in_standalone_mode(self):
        Config.configure_job_executions(mode=JobConfig._STANDALONE_MODE)

        input_cfg_1 = Config.configure_data_node(id="i1", storage_type="pickle", default_data=1, scope=Scope.SCENARIO)
        output_cfg_1 = Config.configure_data_node(id="o1", storage_type="pickle", scope=Scope.SCENARIO)
        task_cfg_1 = Config.configure_task("t1", print, input_cfg_1, output_cfg_1)
        scenario_cfg_1 = Config.configure_scenario("s1", [task_cfg_1], [], Frequency.DAILY)

        Core().run()

        scenario_1 = tp.create_scenario(scenario_cfg_1)
        tp.submit(scenario_1, wait=True)

        with pytest.raises(ConfigurationUpdateBlocked):
            Config.configure_scenario("block_scenario", set([task_cfg_1]))

    def test_get_data_node(self, data_node):
        with mock.patch("src.taipy.core.data._data_manager._DataManager._get") as mck:
            tp.get(data_node.id)
            mck.assert_called_once_with(data_node.id)

    def test_get_data_nodes(self):
        with mock.patch("src.taipy.core.data._data_manager._DataManager._get_all") as mck:
            tp.get_data_nodes()
            mck.assert_called_once_with()

    def test_data_node_exists(self):
        with mock.patch("src.taipy.core.data._data_manager._DataManager._exists") as mck:
            data_node_id = DataNodeId("DATANODE_id")
            tp.exists(data_node_id)
            mck.assert_called_once_with(data_node_id)

    def test_get_cycles(self):
        with mock.patch("src.taipy.core.cycle._cycle_manager._CycleManager._get_all") as mck:
            tp.get_cycles()
            mck.assert_called_once_with()

    def test_cycle_exists(self):
        with mock.patch("src.taipy.core.cycle._cycle_manager._CycleManager._exists") as mck:
            cycle_id = CycleId("CYCLE_id")
            tp.exists(cycle_id)
            mck.assert_called_once_with(cycle_id)

    def test_create_global_data_node(self):
        dn_cfg = DataNodeConfig("id", "pickle", Scope.GLOBAL)
        with mock.patch("src.taipy.core.data._data_manager._DataManager._create_and_set") as mck:
            dn = tp.create_global_data_node(dn_cfg)
            mck.assert_called_once_with(dn_cfg, None, None)

        dn = tp.create_global_data_node(dn_cfg)
        assert dn.scope == Scope.GLOBAL
        assert dn.config_id == dn_cfg.id

        # Create a global data node from the same configuration should return the same data node
        dn_2 = tp.create_global_data_node(dn_cfg)
        assert dn_2.id == dn.id

        dn_cfg.scope = Scope.SCENARIO
        with pytest.raises(DataNodeConfigIsNotGlobal):
            tp.create_global_data_node(dn_cfg)

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

    def test_export_scenario_filesystem(self):
        shutil.rmtree("./tmp", ignore_errors=True)

        input_cfg_1 = Config.configure_data_node(id="i1", storage_type="pickle", default_data=1, scope=Scope.SCENARIO)
        output_cfg_1 = Config.configure_data_node(id="o1", storage_type="pickle", scope=Scope.SCENARIO)
        task_cfg_1 = Config.configure_task("t1", print, input_cfg_1, output_cfg_1)
        scenario_cfg_1 = Config.configure_scenario("s1", [task_cfg_1], [], Frequency.DAILY)

        input_cfg_2 = Config.configure_data_node(id="i2", storage_type="pickle", default_data=2, scope=Scope.SCENARIO)
        output_cfg_2 = Config.configure_data_node(id="o2", storage_type="pickle", scope=Scope.SCENARIO)
        task_cfg_2 = Config.configure_task("t2", print, input_cfg_2, output_cfg_2)
        scenario_cfg_2 = Config.configure_scenario("s2", [task_cfg_2], [], Frequency.DAILY)

        scenario_1 = tp.create_scenario(scenario_cfg_1)
        job_1 = tp.submit(scenario_1)[0]

        # Export scenario 1
        tp.export_scenario(scenario_1.id, "./tmp/exp_scenario_1")
        assert sorted(os.listdir("./tmp/exp_scenario_1/data_nodes")) == sorted(
            [f"{scenario_1.i1.id}.json", f"{scenario_1.o1.id}.json"]
        )
        assert sorted(os.listdir("./tmp/exp_scenario_1/tasks")) == sorted([f"{scenario_1.t1.id}.json"])
        assert sorted(os.listdir("./tmp/exp_scenario_1/scenarios")) == sorted([f"{scenario_1.id}.json"])
        assert sorted(os.listdir("./tmp/exp_scenario_1/jobs")) == sorted([f"{job_1.id}.json"])
        assert sorted(os.listdir("./tmp/exp_scenario_1/cycles")) == sorted([f"{scenario_1.cycle.id}.json"])

        scenario_2 = tp.create_scenario(scenario_cfg_2)
        job_2 = tp.submit(scenario_2)[0]

        # Export scenario 2
        scenario_2.export(pathlib.Path.cwd() / "./tmp/exp_scenario_2")
        assert sorted(os.listdir("./tmp/exp_scenario_2/data_nodes")) == sorted(
            [f"{scenario_2.i2.id}.json", f"{scenario_2.o2.id}.json"]
        )
        assert sorted(os.listdir("./tmp/exp_scenario_2/tasks")) == sorted([f"{scenario_2.t2.id}.json"])
        assert sorted(os.listdir("./tmp/exp_scenario_2/scenarios")) == sorted([f"{scenario_2.id}.json"])
        assert sorted(os.listdir("./tmp/exp_scenario_2/jobs")) == sorted([f"{job_2.id}.json"])
        assert sorted(os.listdir("./tmp/exp_scenario_2/cycles")) == sorted([f"{scenario_2.cycle.id}.json"])

        # Export scenario 2 into the folder containing scenario 1 files
        tp.export_scenario(scenario_2.id, "./tmp/exp_scenario_1")
        # Should have the files as scenario 1 only
        assert sorted(os.listdir("./tmp/exp_scenario_1/tasks")) == sorted([f"{scenario_2.t2.id}.json"])
        assert sorted(os.listdir("./tmp/exp_scenario_1/scenarios")) == sorted([f"{scenario_2.id}.json"])
        assert sorted(os.listdir("./tmp/exp_scenario_1/jobs")) == sorted([f"{job_2.id}.json"])
        assert sorted(os.listdir("./tmp/exp_scenario_1/cycles")) == sorted([f"{scenario_2.cycle.id}.json"])

        with pytest.raises(InvalidExportPath):
            tp.export_scenario(scenario_2.id, Config.core.storage_folder)

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
        dn_config_4 = Config.configure_data_node(id="d4", storage_type="in_memory", scope=Scope.SCENARIO)
        task_config_1 = Config.configure_task("t1", print, dn_config_1, dn_config_2)
        task_config_2 = Config.configure_task("t2", print, dn_config_2, dn_config_3)
        scenario_cfg_1 = Config.configure_scenario("s1", [task_config_1, task_config_2], [dn_config_4], Frequency.DAILY)

        scenario = tp.create_scenario(scenario_cfg_1)
        tasks = scenario.tasks

        expected_parents = {
            "scenario": {scenario},
            "task": {tasks["t1"]},
        }
        parents = tp.get_parents(scenario.tasks["t1"].data_nodes["d1"])
        assert_result_parents_and_expected_parents(parents, expected_parents)

        expected_parents = {
            "scenario": {scenario},
            "task": {tasks["t1"], tasks["t2"]},
        }
        parents = tp.get_parents(scenario.tasks["t1"].data_nodes["d2"])
        assert_result_parents_and_expected_parents(parents, expected_parents)

        expected_parents = {"scenario": {scenario}, "task": {tasks["t2"]}}
        parents = tp.get_parents(scenario.tasks["t2"].data_nodes["d3"])
        assert_result_parents_and_expected_parents(parents, expected_parents)

        expected_parents = {"scenario": {scenario}}
        parents = tp.get_parents(scenario.tasks["t1"])
        assert_result_parents_and_expected_parents(parents, expected_parents)

        expected_parents = {"scenario": {scenario}}
        parents = tp.get_parents(scenario.tasks["t2"])
        assert_result_parents_and_expected_parents(parents, expected_parents)

        expected_parents = {"scenario": {scenario}}
        parents = tp.get_parents(scenario.additional_data_nodes["d4"])
        assert_result_parents_and_expected_parents(parents, expected_parents)

        expected_parents = {}
        parents = tp.get_parents(scenario)
        assert_result_parents_and_expected_parents(parents, expected_parents)

        expected_parents = {}
        parents = tp.get_parents(scenario.cycle)
        assert_result_parents_and_expected_parents(parents, expected_parents)

    def test_get_cycles_scenarios(self):
        scenario_cfg_1 = Config.configure_scenario(
            "s1",
            set(),
            set(),
            Frequency.DAILY,
        )
        scenario_cfg_2 = Config.configure_scenario("s2", set(), set(), Frequency.WEEKLY)
        scenario_cfg_3 = Config.configure_scenario("s3", set(), set(), Frequency.MONTHLY)
        scenario_cfg_4 = Config.configure_scenario("s4", set(), set(), Frequency.YEARLY)
        scenario_cfg_5 = Config.configure_scenario("s5", set(), set(), None)

        now = datetime.datetime.now()
        scenario_1_1 = tp.create_scenario(scenario_cfg_1, now)
        scenario_1_2 = tp.create_scenario(scenario_cfg_1, datetime.datetime.now())
        scenario_1_3 = tp.create_scenario(scenario_cfg_1, now + datetime.timedelta(days=1))
        scenario_1_4 = tp.create_scenario(scenario_cfg_1, now + datetime.timedelta(days=8))
        scenario_1_5 = tp.create_scenario(scenario_cfg_1, now + datetime.timedelta(days=25))
        scenario_2 = tp.create_scenario(scenario_cfg_2)
        scenario_3 = tp.create_scenario(scenario_cfg_3)
        scenario_4 = tp.create_scenario(scenario_cfg_4)
        scenario_5_1 = tp.create_scenario(scenario_cfg_5)
        scenario_5_2 = tp.create_scenario(scenario_cfg_5)
        scenario_5_3 = tp.create_scenario(scenario_cfg_5)

        expected_cycles_scenarios = {
            scenario_1_1.cycle: [scenario_1_1.id, scenario_1_2.id],
            scenario_1_3.cycle: [scenario_1_3.id],
            scenario_1_4.cycle: [scenario_1_4.id],
            scenario_1_5.cycle: [scenario_1_5.id],
            scenario_2.cycle: [scenario_2.id],
            scenario_3.cycle: [scenario_3.id],
            scenario_4.cycle: [scenario_4.id],
            None: [scenario_5_1.id, scenario_5_2.id, scenario_5_3.id],
        }

        cycles_scenarios = tp.get_cycles_scenarios()

        assert expected_cycles_scenarios.keys() == cycles_scenarios.keys()
        for cycle, scenarios in cycles_scenarios.items():
            expected_scenarios = expected_cycles_scenarios[cycle]
            assert sorted([scenario.id for scenario in scenarios]) == sorted(expected_scenarios)

    def test_get_entities_by_config_id(self):
        scenario_config_1 = Config.configure_scenario("s1", sequence_configs=[])
        scenario_config_2 = Config.configure_scenario("s2", sequence_configs=[])

        s_1_1 = tp.create_scenario(scenario_config_1)
        s_1_2 = tp.create_scenario(scenario_config_1)
        s_1_3 = tp.create_scenario(scenario_config_1)

        assert len(tp.get_scenarios()) == 3

        s_2_1 = tp.create_scenario(scenario_config_2)
        s_2_2 = tp.create_scenario(scenario_config_2)
        assert len(tp.get_scenarios()) == 5

        s1_scenarios = tp.get_entities_by_config_id(scenario_config_1.id)
        assert len(s1_scenarios) == 3
        assert sorted([s_1_1.id, s_1_2.id, s_1_3.id]) == sorted([scenario.id for scenario in s1_scenarios])

        s2_scenarios = tp.get_entities_by_config_id(scenario_config_2.id)
        assert len(s2_scenarios) == 2
        assert sorted([s_2_1.id, s_2_2.id]) == sorted([scenario.id for scenario in s2_scenarios])

    def test_get_entities_by_config_id_in_multiple_versions_environment(self):
        scenario_config_1 = Config.configure_scenario("s1", sequence_configs=[])
        scenario_config_2 = Config.configure_scenario("s2", sequence_configs=[])

        _VersionManager._set_experiment_version("1.0")
        tp.create_scenario(scenario_config_1)
        tp.create_scenario(scenario_config_1)
        tp.create_scenario(scenario_config_1)
        tp.create_scenario(scenario_config_2)
        tp.create_scenario(scenario_config_2)
        assert len(tp.get_scenarios()) == 5
        assert len(tp.get_entities_by_config_id(scenario_config_1.id)) == 3
        assert len(tp.get_entities_by_config_id(scenario_config_2.id)) == 2

        _VersionManager._set_experiment_version("2.0")
        tp.create_scenario(scenario_config_1)
        tp.create_scenario(scenario_config_1)
        tp.create_scenario(scenario_config_1)
        tp.create_scenario(scenario_config_2)
        tp.create_scenario(scenario_config_2)
        assert len(tp.get_scenarios()) == 5
        assert len(tp.get_entities_by_config_id(scenario_config_1.id)) == 3
        assert len(tp.get_entities_by_config_id(scenario_config_2.id)) == 2
