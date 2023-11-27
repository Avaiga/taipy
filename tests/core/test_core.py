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

from unittest.mock import patch

import pytest

from src.taipy.core import Core
from src.taipy.core._orchestrator._dispatcher import _DevelopmentJobDispatcher, _StandaloneJobDispatcher
from src.taipy.core._orchestrator._orchestrator import _Orchestrator
from src.taipy.core._orchestrator._orchestrator_factory import _OrchestratorFactory
from src.taipy.core.config.job_config import JobConfig
from src.taipy.core.exceptions.exceptions import CoreServiceIsAlreadyRunning
from taipy.config import Config
from taipy.config.exceptions.exceptions import ConfigurationUpdateBlocked


class TestCore:
    def test_run_core_trigger_config_check(self, caplog):
        Config.configure_data_node(id="d0", storage_type="toto")
        with patch("sys.argv", ["prog"]):
            with pytest.raises(SystemExit):
                core = Core()
                core.run()
        expected_error_message = (
            "`storage_type` field of DataNodeConfig `d0` must be either csv, sql_table,"
            " sql, mongo_collection, pickle, excel, generic, json, parquet, or in_memory."
            ' Current value of property `storage_type` is "toto".'
        )
        assert expected_error_message in caplog.text
        core.stop()

    def test_run_core_as_a_service_development_mode(self):
        _OrchestratorFactory._dispatcher = None

        with patch("sys.argv", ["prog"]):
            core = Core()
            assert core._orchestrator is None
            assert core._dispatcher is None
            assert _OrchestratorFactory._dispatcher is None

            core.run()
            assert core._orchestrator is not None
            assert core._orchestrator == _Orchestrator
            assert _OrchestratorFactory._orchestrator is not None
            assert _OrchestratorFactory._orchestrator == _Orchestrator
            assert core._dispatcher is not None
            assert isinstance(core._dispatcher, _DevelopmentJobDispatcher)
            assert isinstance(_OrchestratorFactory._dispatcher, _DevelopmentJobDispatcher)
            core.stop()

    def test_run_core_as_a_service_standalone_mode(self):
        _OrchestratorFactory._dispatcher = None

        with patch("sys.argv", ["prog"]):
            core = Core()
            assert core._orchestrator is None

            assert core._dispatcher is None
            assert _OrchestratorFactory._dispatcher is None

            Config.configure_job_executions(mode=JobConfig._STANDALONE_MODE, max_nb_of_workers=2)
            core.run()
            assert core._orchestrator is not None
            assert core._orchestrator == _Orchestrator
            assert _OrchestratorFactory._orchestrator is not None
            assert _OrchestratorFactory._orchestrator == _Orchestrator
            assert core._dispatcher is not None
            assert isinstance(core._dispatcher, _StandaloneJobDispatcher)
            assert isinstance(_OrchestratorFactory._dispatcher, _StandaloneJobDispatcher)
            assert core._dispatcher.is_running()
            assert _OrchestratorFactory._dispatcher.is_running()
            core.stop()

    def test_core_service_can_only_be_run_once(self):
        core_instance_1 = Core()
        core_instance_2 = Core()

        core_instance_1.run()

        with pytest.raises(CoreServiceIsAlreadyRunning):
            core_instance_1.run()
        with pytest.raises(CoreServiceIsAlreadyRunning):
            core_instance_2.run()

        # Stop the Core service and run it again should work
        core_instance_1.stop()

        core_instance_1.run()
        core_instance_1.stop()
        core_instance_2.run()
        core_instance_2.stop()

    def test_block_config_update_when_core_service_is_running_development_mode(self):
        _OrchestratorFactory._dispatcher = None

        with patch("sys.argv", ["prog"]):
            core = Core()
            core.run()
            with pytest.raises(ConfigurationUpdateBlocked):
                Config.configure_data_node(id="i1")
            core.stop()

    def test_block_config_update_when_core_service_is_running_standalone_mode(self):
        _OrchestratorFactory._dispatcher = None

        with patch("sys.argv", ["prog"]):
            core = Core()
            Config.configure_job_executions(mode=JobConfig._STANDALONE_MODE, max_nb_of_workers=2)
            core.run()
            with pytest.raises(ConfigurationUpdateBlocked):
                Config.configure_data_node(id="i1")
            core.stop()
