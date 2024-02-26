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

from taipy.config import Config
from taipy.core import taipy
from taipy.core._orchestrator._orchestrator_factory import _OrchestratorFactory
from taipy.core.job._job_manager_factory import _JobManagerFactory


def nothing(*args, **kwargs):
    pass


def test_is_not_blocked_task_single_input():
    inp = Config.configure_data_node("inp", default_data="DEFAULT")
    t = Config.configure_task("the_task", nothing, [inp], [])
    sc_conf = Config.configure_scenario("scenario", [t])
    scenario = taipy.create_scenario(sc_conf)
    orchestrator = _OrchestratorFactory._build_orchestrator()

    res = orchestrator._is_blocked(scenario.the_task)

    assert res is False


def test_is_not_blocked_task_multiple_input_and_output():
    dn_0 = Config.configure_data_node("in_0", default_data="THIS")
    dn_1 = Config.configure_data_node("in_1", default_data="IS")
    dn_2 = Config.configure_data_node("in_2", default_data="DEFAULT")
    out = Config.configure_data_node("output_dn")
    t = Config.configure_task("the_task", nothing, [dn_0, dn_1, dn_2], [out])
    sc_conf = Config.configure_scenario("scenario", [t])
    scenario = taipy.create_scenario(sc_conf)
    orchestrator = _OrchestratorFactory._build_orchestrator()

    res = orchestrator._is_blocked(scenario.the_task)

    assert res is False


def test_is_blocked_task_single_input_no_data():
    inp = Config.configure_data_node("inp")
    t = Config.configure_task("the_task", nothing, [inp], [])
    sc_conf = Config.configure_scenario("scenario", [t])
    scenario = taipy.create_scenario(sc_conf)
    orchestrator = _OrchestratorFactory._build_orchestrator()

    res = orchestrator._is_blocked(scenario.the_task)

    assert res is True


def test_is_blocked_task_single_input_edit_in_progress():
    input_dn_cfg = Config.configure_data_node("inp", default_data=51)
    t_cfg = Config.configure_task("the_task", nothing, [input_dn_cfg])
    sc_conf = Config.configure_scenario("scenario", [t_cfg])
    scenario = taipy.create_scenario(sc_conf)
    orchestrator = _OrchestratorFactory._build_orchestrator()
    scenario.inp.lock_edit()

    res = orchestrator._is_blocked(scenario.the_task)

    assert res is True


def test_is_blocked_task_multiple_input_no_data():
    dn_0 = Config.configure_data_node("input_0", default_data="THIS")
    dn_1 = Config.configure_data_node("input_1")
    out = Config.configure_data_node("output_dn")
    t_config = Config.configure_task("the_task", nothing, [dn_0, dn_1], [out])
    sc_conf = Config.configure_scenario("scenario", [t_config])
    scenario = taipy.create_scenario(sc_conf)
    orchestrator = _OrchestratorFactory._build_orchestrator()

    res = orchestrator._is_blocked(scenario.the_task)

    assert res is True


def test_is_not_blocked_job_single_input():
    inp = Config.configure_data_node("inp", default_data="DEFAULT")
    t = Config.configure_task("the_task", nothing, [inp], [])
    sc_conf = Config.configure_scenario("scenario", [t])
    scenario = taipy.create_scenario(sc_conf)
    orchestrator = _OrchestratorFactory._build_orchestrator()
    job = _JobManagerFactory._build_manager()._create(scenario.the_task, [nothing], "s_id", "e_id")

    res = orchestrator._is_blocked(job)

    assert res is False


def test_is_not_blocked_job_multiple_input_and_output():
    in_0 = Config.configure_data_node("in_0", default_data="THIS")
    in_1 = Config.configure_data_node("in_1", default_data="IS")
    out = Config.configure_data_node("output_dn")
    t = Config.configure_task("the_task", nothing, [in_0, in_1], [out])
    sc_conf = Config.configure_scenario("scenario", [t])
    scenario = taipy.create_scenario(sc_conf)
    orchestrator = _OrchestratorFactory._build_orchestrator()
    job = _JobManagerFactory._build_manager()._create(scenario.the_task, [nothing], "s_id", "e_id")

    res = orchestrator._is_blocked(job)

    assert res is False


def test_is_blocked_job_single_input_no_data():
    inp = Config.configure_data_node("inp")
    t = Config.configure_task("the_task", nothing, [inp], [])
    sc_conf = Config.configure_scenario("scenario", [t])
    scenario = taipy.create_scenario(sc_conf)
    orchestrator = _OrchestratorFactory._build_orchestrator()
    job = _JobManagerFactory._build_manager()._create(scenario.the_task, [nothing], "s_id", "e_id")

    res = orchestrator._is_blocked(job)

    assert res is True


def test_is_blocked_job_single_input_edit_in_progress():
    input_dn_cfg = Config.configure_data_node("inp", default_data="foo")
    task_cfg = Config.configure_task("the_task", nothing, [input_dn_cfg])
    sc_conf = Config.configure_scenario("scenario", [task_cfg])
    scenario = taipy.create_scenario(sc_conf)
    orchestrator = _OrchestratorFactory._build_orchestrator()
    scenario.inp.lock_edit()
    job = _JobManagerFactory._build_manager()._create(scenario.the_task, [nothing], "s_id", "e_id")

    res = orchestrator._is_blocked(job)

    assert res is True


def test_is_blocked_job_multiple_input_no_data():
    dn_0 = Config.configure_data_node("in_0", default_data="THIS")
    dn_1 = Config.configure_data_node("in_1", default_data="IS")
    dn_2 = Config.configure_data_node("in_2")
    out = Config.configure_data_node("output_dn")
    t = Config.configure_task("the_task", nothing, [dn_0, dn_1, dn_2], [out])
    sc_conf = Config.configure_scenario("scenario", [t])
    scenario = taipy.create_scenario(sc_conf)
    orchestrator = _OrchestratorFactory._build_orchestrator()
    job = _JobManagerFactory._build_manager()._create(scenario.the_task, [nothing], "s_id", "e_id")

    res = orchestrator._is_blocked(job)

    assert res is True
