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

import pytest

from src.taipy.core import Core
from src.taipy.core._scheduler._dispatcher import _DevelopmentJobDispatcher, _StandaloneJobDispatcher
from src.taipy.core._scheduler._scheduler import _Scheduler
from src.taipy.core._scheduler._scheduler_factory import _SchedulerFactory
from src.taipy.core.config.job_config import JobConfig
from taipy.config import Config
from taipy.config.exceptions.exceptions import ConfigurationUpdateBlocked


class TestCore:
    def test_run_core_as_a_service_development_mode(self):
        _SchedulerFactory._dispatcher = None

        core = Core()
        assert core._scheduler is not None
        assert core._scheduler == _Scheduler
        assert _SchedulerFactory._scheduler is not None
        assert _SchedulerFactory._scheduler == _Scheduler

        assert core._dispatcher is None
        assert _SchedulerFactory._dispatcher is None

        Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)
        core.run()
        assert core._dispatcher is not None
        assert isinstance(core._dispatcher, _DevelopmentJobDispatcher)
        assert isinstance(_SchedulerFactory._dispatcher, _DevelopmentJobDispatcher)

    def test_run_core_as_a_service_standalone_mode(self):
        _SchedulerFactory._dispatcher = None

        core = Core()
        assert core._scheduler is not None
        assert core._scheduler == _Scheduler
        assert _SchedulerFactory._scheduler is not None
        assert _SchedulerFactory._scheduler == _Scheduler

        assert core._dispatcher is None
        assert _SchedulerFactory._dispatcher is None

        Config.configure_job_executions(mode=JobConfig._STANDALONE_MODE, max_nb_of_workers=2)
        core.run()
        assert core._dispatcher is not None
        assert isinstance(core._dispatcher, _StandaloneJobDispatcher)
        assert isinstance(_SchedulerFactory._dispatcher, _StandaloneJobDispatcher)
        assert core._dispatcher.is_running()
        assert _SchedulerFactory._dispatcher.is_running()

    def test_block_config_update_when_core_service_is_running_development_mode(self):
        _SchedulerFactory._dispatcher = None

        core = Core()
        Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)
        core.run()
        with pytest.raises(ConfigurationUpdateBlocked):
            Config.configure_data_node(id="i1")

    def test_block_config_update_when_core_service_is_running_standalone_mode(self):
        _SchedulerFactory._dispatcher = None

        core = Core()
        Config.configure_job_executions(mode=JobConfig._STANDALONE_MODE, max_nb_of_workers=2)
        core.run()
        with pytest.raises(ConfigurationUpdateBlocked):
            Config.configure_data_node(id="i1")
