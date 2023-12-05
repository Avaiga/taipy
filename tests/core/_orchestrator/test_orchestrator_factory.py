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

from unittest import mock

import pytest
from taipy.config import Config
from taipy.core._orchestrator._dispatcher import _DevelopmentJobDispatcher, _JobDispatcher, _StandaloneJobDispatcher
from taipy.core._orchestrator._orchestrator import _Orchestrator
from taipy.core._orchestrator._orchestrator_factory import _OrchestratorFactory
from taipy.core.config.job_config import JobConfig
from taipy.core.exceptions.exceptions import OrchestratorNotBuilt


def test_build_orchestrator():
    _OrchestratorFactory._orchestrator = None
    _OrchestratorFactory._dispatcher = None

    assert _OrchestratorFactory._orchestrator is None
    assert _OrchestratorFactory._dispatcher is None

    orchestrator = _OrchestratorFactory._build_orchestrator()
    assert orchestrator == _Orchestrator
    assert _OrchestratorFactory._orchestrator == _Orchestrator
    dispatcher = _OrchestratorFactory._build_dispatcher()
    assert isinstance(dispatcher, _JobDispatcher)
    assert isinstance(_OrchestratorFactory._dispatcher, _JobDispatcher)

    _OrchestratorFactory._orchestrator = None
    assert _OrchestratorFactory._orchestrator is None
    assert _OrchestratorFactory._dispatcher is not None

    with mock.patch(
        "taipy.core._orchestrator._orchestrator_factory._OrchestratorFactory._build_dispatcher"
    ) as build_dispatcher, mock.patch("taipy.core._orchestrator._orchestrator._Orchestrator.initialize") as initialize:
        orchestrator = _OrchestratorFactory._build_orchestrator()
        assert orchestrator == _Orchestrator
        assert _OrchestratorFactory._orchestrator == _Orchestrator
        build_dispatcher.assert_not_called()
        initialize.assert_called_once()


def test_build_development_dispatcher():
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)
    _OrchestratorFactory._orchestrator = None
    _OrchestratorFactory._dispatcher = None

    assert _OrchestratorFactory._orchestrator is None
    assert _OrchestratorFactory._dispatcher is None

    with pytest.raises(OrchestratorNotBuilt):
        _OrchestratorFactory._build_dispatcher()

    _OrchestratorFactory._build_orchestrator()
    assert _OrchestratorFactory._orchestrator is not None
    assert _OrchestratorFactory._dispatcher is None

    _OrchestratorFactory._build_dispatcher()
    assert isinstance(_OrchestratorFactory._dispatcher, _DevelopmentJobDispatcher)


def test_build_standalone_dispatcher():
    Config.configure_job_executions(mode=JobConfig._STANDALONE_MODE, max_nb_of_workers=2)
    _OrchestratorFactory._build_dispatcher()
    assert isinstance(_OrchestratorFactory._dispatcher, _StandaloneJobDispatcher)
    assert not isinstance(_OrchestratorFactory._dispatcher, _DevelopmentJobDispatcher)
    assert _OrchestratorFactory._dispatcher.is_running()
    assert _OrchestratorFactory._dispatcher._nb_available_workers == 2
    _OrchestratorFactory._dispatcher._nb_available_workers = 1

    _OrchestratorFactory._build_dispatcher(force_restart=False)
    assert _OrchestratorFactory._dispatcher.is_running()
    assert _OrchestratorFactory._dispatcher._nb_available_workers == 1

    _OrchestratorFactory._build_dispatcher(force_restart=True)
    assert _OrchestratorFactory._dispatcher.is_running()
    assert _OrchestratorFactory._dispatcher._nb_available_workers == 2
