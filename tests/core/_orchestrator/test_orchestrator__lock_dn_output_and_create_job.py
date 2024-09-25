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

from taipy.common.config import Config
from taipy.core import taipy
from taipy.core._orchestrator._orchestrator import _Orchestrator
from taipy.core._orchestrator._orchestrator_factory import _OrchestratorFactory


def nothing(*args, **kwargs):
    pass


def test_lock_dn_and_create_job():
    t = Config.configure_task("no_output", nothing, [], [])
    sc_conf = Config.configure_scenario("scenario", [t])
    scenario = taipy.create_scenario(sc_conf)
    task = scenario.no_output
    s_id = "submit_id"
    entity_id = "scenario_id"
    cbs = None
    force = False

    job = _OrchestratorFactory._build_orchestrator()._lock_dn_output_and_create_job(task, s_id, entity_id, cbs, force)

    assert job.submit_id == s_id
    assert job.submit_entity_id == entity_id
    assert job.task == task
    assert not job.force
    assert len(job._subscribers) == 1
    assert job._subscribers[0] == _Orchestrator._on_status_change
    assert len(taipy.get_jobs()) == 1


def test_lock_dn_and_create_job_with_callback_and_force():
    t = Config.configure_task("no_output", nothing, [], [])
    sc_conf = Config.configure_scenario("scenario", [t])
    scenario = taipy.create_scenario(sc_conf)
    task = scenario.no_output
    s_id = "submit_id"
    entity_id = "scenario_id"
    cbs = [nothing]
    force = True

    job = _OrchestratorFactory._build_orchestrator()._lock_dn_output_and_create_job(task, s_id, entity_id, cbs, force)

    assert job.submit_id == s_id
    assert job.submit_entity_id == entity_id
    assert job.task == task
    assert job.force
    assert len(job._subscribers) == 2
    assert job._subscribers[0] == nothing
    assert job._subscribers[1] == _Orchestrator._on_status_change
    assert len(taipy.get_jobs()) == 1


def test_lock_dn_and_create_job_one_output():
    dn = Config.configure_data_node("output_dn")
    t = Config.configure_task("one_output", nothing, [], [dn])
    sc_conf = Config.configure_scenario("scenario", [t])
    scenario = taipy.create_scenario(sc_conf)
    orchestrator = _OrchestratorFactory._build_orchestrator()
    orchestrator._lock_dn_output_and_create_job(scenario.one_output, "submit_id", "scenario_id")

    assert scenario.output_dn.edit_in_progress


def test_lock_dn_and_create_job_multiple_outputs_one_input():
    dn_0 = Config.configure_data_node("input_0", default_data=0)
    dn_1 = Config.configure_data_node("output_1")
    dn_2 = Config.configure_data_node("output_2")
    dn_3 = Config.configure_data_node("output_3")
    t = Config.configure_task("one_output", nothing, [dn_0], [dn_1, dn_2, dn_3])
    sc_conf = Config.configure_scenario("scenario", [t])
    scenario = taipy.create_scenario(sc_conf)
    orchestrator = _OrchestratorFactory._build_orchestrator()
    orchestrator._lock_dn_output_and_create_job(scenario.one_output, "submit_id", "scenario_id")

    assert not scenario.input_0.edit_in_progress
    assert scenario.input_0.is_ready_for_reading
    assert scenario.output_1.edit_in_progress
    assert not scenario.output_1.is_ready_for_reading
    assert scenario.output_2.edit_in_progress
    assert not scenario.output_2.is_ready_for_reading
    assert scenario.output_3.edit_in_progress
    assert not scenario.output_3.is_ready_for_reading
