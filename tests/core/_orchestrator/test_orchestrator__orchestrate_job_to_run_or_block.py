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
from unittest.mock import patch

from taipy import Status
from taipy.config import Config
from taipy.core import taipy
from taipy.core._orchestrator._orchestrator_factory import _OrchestratorFactory
from taipy.core.job._job_manager_factory import _JobManagerFactory


def nothing(*args, **kwargs):
    pass


def test_orchestrate_job_to_run_or_block_single_blocked_job():
    with patch("sys.argv", ["prog"]):
        inp = Config.configure_data_node("inp")  # No default data
        t = Config.configure_task("the_task", nothing, [inp], [])
        sc_conf = Config.configure_scenario("scenario", [t])
        scenario = taipy.create_scenario(sc_conf)
        orchestrator = _OrchestratorFactory._build_orchestrator()
        job = _JobManagerFactory._build_manager()._create(scenario.the_task, [nothing], "s_id", "e_id")

        orchestrator._orchestrate_job_to_run_or_block([job])

        assert len(orchestrator.blocked_jobs) == 1
        assert job.status == Status.BLOCKED
        assert orchestrator.jobs_to_run.empty()


def test_orchestrate_job_to_run_or_block_single_pending_job():
    with patch("sys.argv", ["prog"]):
        inp = Config.configure_data_node("inp", default_data=1)  # Has default data
        t = Config.configure_task("my_task", nothing, [inp], [])
        sc_conf = Config.configure_scenario("scenario", [t])
        scenario = taipy.create_scenario(sc_conf)
        orchestrator = _OrchestratorFactory._build_orchestrator()
        job = _JobManagerFactory._build_manager()._create(scenario.my_task, [nothing], "s_id", "e_id")

        orchestrator._orchestrate_job_to_run_or_block([job])

        assert len(orchestrator.blocked_jobs) == 0
        assert job.status == Status.PENDING
        assert orchestrator.jobs_to_run.qsize() == 1


def test_orchestrate_job_to_run_or_block_multiple_jobs():
    with patch("sys.argv", ["prog"]):
        input = Config.configure_data_node("input_dn", default_data=1)  # Has default data
        intermediate = Config.configure_data_node("intermediate")  # Has default data
        output = Config.configure_data_node("output_dn")  # Has default data
        t1 = Config.configure_task("my_task_1", nothing, [input], [])
        t2 = Config.configure_task("my_task_2", nothing, [], [intermediate])
        t3 = Config.configure_task("my_task_3", nothing, [intermediate], [output])
        sc_conf = Config.configure_scenario("scenario", [t1, t2, t3])
        scenario = taipy.create_scenario(sc_conf)
        orchestrator = _OrchestratorFactory._build_orchestrator()
        job_1 = _JobManagerFactory._build_manager()._create(scenario.my_task_1, [nothing], "s_id", "e_id")
        job_2 = _JobManagerFactory._build_manager()._create(scenario.my_task_2, [nothing], "s_id", "e_id")
        job_3 = _JobManagerFactory._build_manager()._create(scenario.my_task_3, [nothing], "s_id", "e_id")

        orchestrator._orchestrate_job_to_run_or_block([job_1, job_2, job_3])

        assert orchestrator.jobs_to_run.qsize() == 2
        assert job_1.status == Status.PENDING
        assert job_2.status == Status.PENDING
        assert len(orchestrator.blocked_jobs) == 1
        assert job_3.status == Status.BLOCKED


def test_orchestrate_job_to_run_or_block__no_job_doesnot_raise_error():
    orchestrator = _OrchestratorFactory._build_orchestrator()

    orchestrator._orchestrate_job_to_run_or_block([])
