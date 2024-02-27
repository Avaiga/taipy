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

from unittest import mock

import pytest

from taipy.config import Config
from taipy.core._orchestrator._dispatcher import _DevelopmentJobDispatcher, _StandaloneJobDispatcher
from taipy.core._orchestrator._orchestrator import _Orchestrator
from taipy.core._orchestrator._orchestrator_factory import _OrchestratorFactory
from taipy.core.config.job_config import JobConfig
from taipy.core.exceptions import ModeNotAvailable
from taipy.core.exceptions.exceptions import OrchestratorNotBuilt


def test_build_orchestrator():
    _OrchestratorFactory._orchestrator = None
    _OrchestratorFactory._dispatcher = None

    with mock.patch("taipy.core._orchestrator._orchestrator_factory._OrchestratorFactory._build_dispatcher") as bd:
        with mock.patch("taipy.core._orchestrator._orchestrator._Orchestrator.initialize") as initialize:
            orchestrator = _OrchestratorFactory._build_orchestrator()
            _OrchestratorFactory._build_orchestrator()  # Call it one more time!
            assert orchestrator == _Orchestrator
            assert _OrchestratorFactory._orchestrator == _Orchestrator
            initialize.assert_called_once()
            bd.assert_not_called()


def test_build_dispatcher_no_orchestrator():
    _OrchestratorFactory._orchestrator = None
    _OrchestratorFactory._dispatcher = None
    with pytest.raises(OrchestratorNotBuilt):
        _OrchestratorFactory._build_dispatcher()
        assert _OrchestratorFactory._dispatcher is None


def test_build_dispatcher_default():
    _OrchestratorFactory._orchestrator = None
    _OrchestratorFactory._dispatcher = None
    _OrchestratorFactory._build_orchestrator()
    _OrchestratorFactory._build_dispatcher()
    assert isinstance(_OrchestratorFactory._dispatcher, _DevelopmentJobDispatcher)


def test_build_development_dispatcher():
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)
    _OrchestratorFactory._orchestrator = None
    _OrchestratorFactory._dispatcher = None
    _OrchestratorFactory._build_orchestrator()
    _OrchestratorFactory._build_dispatcher()
    assert isinstance(_OrchestratorFactory._dispatcher, _DevelopmentJobDispatcher)


@pytest.mark.standalone
def test_build_standalone_dispatcher():
    Config.configure_job_executions(mode=JobConfig._STANDALONE_MODE)
    _OrchestratorFactory._orchestrator = None
    _OrchestratorFactory._dispatcher = None
    _OrchestratorFactory._build_orchestrator()
    _OrchestratorFactory._build_dispatcher()
    assert isinstance(_OrchestratorFactory._dispatcher, _StandaloneJobDispatcher)
    assert _OrchestratorFactory._dispatcher.is_running()
    _OrchestratorFactory._dispatcher.stop()


@pytest.mark.standalone
def test_rebuild_standalone_dispatcher_and_force_restart():
    Config.configure_job_executions(mode=JobConfig._STANDALONE_MODE)
    _OrchestratorFactory._build_orchestrator()

    with mock.patch("taipy.core._orchestrator._dispatcher._job_dispatcher._JobDispatcher.start") as start_mock:
        with mock.patch("taipy.core._orchestrator._dispatcher._job_dispatcher._JobDispatcher.stop") as stop_mock:
            _OrchestratorFactory._build_dispatcher()
            assert isinstance(_OrchestratorFactory._dispatcher, _StandaloneJobDispatcher)
            start_mock.assert_called_once()
            stop_mock.assert_not_called()

    with mock.patch("taipy.core._orchestrator._dispatcher._job_dispatcher._JobDispatcher.start") as start_mock:
        with mock.patch("taipy.core._orchestrator._dispatcher._job_dispatcher._JobDispatcher.stop") as stop_mock:
            _OrchestratorFactory._build_dispatcher()  # Default force_restart=False
            assert isinstance(_OrchestratorFactory._dispatcher, _StandaloneJobDispatcher)
            stop_mock.assert_not_called()
            start_mock.assert_not_called()

            _OrchestratorFactory._build_dispatcher(force_restart=False)
            assert isinstance(_OrchestratorFactory._dispatcher, _StandaloneJobDispatcher)
            stop_mock.assert_not_called()
            start_mock.assert_not_called()

            _OrchestratorFactory._build_dispatcher(force_restart=True)
            assert isinstance(_OrchestratorFactory._dispatcher, _StandaloneJobDispatcher)
            stop_mock.assert_called_once()
            start_mock.assert_called_once()
    _OrchestratorFactory._dispatcher.stop()


def test_build_unknown_dispatcher():
    Config.configure_job_executions(mode="UNKNOWN")
    _OrchestratorFactory._build_orchestrator()
    with pytest.raises(ModeNotAvailable):
        _OrchestratorFactory._build_dispatcher()
        assert _OrchestratorFactory._dispatcher is None


def test_remove_dispatcher_not_built():
    _OrchestratorFactory._dispatcher = None
    _OrchestratorFactory._remove_dispatcher()
    assert _OrchestratorFactory._dispatcher is None


def test_remove_dispatcher_development():
    _OrchestratorFactory._build_orchestrator()
    _OrchestratorFactory._build_dispatcher()
    assert _OrchestratorFactory._dispatcher is not None
    _OrchestratorFactory._remove_dispatcher()
    assert _OrchestratorFactory._dispatcher is None


@pytest.mark.standalone
def test_remove_dispatcher_standalone():
    Config.configure_job_executions(mode=JobConfig._STANDALONE_MODE)
    _OrchestratorFactory._build_orchestrator()
    _OrchestratorFactory._build_dispatcher()
    assert _OrchestratorFactory._dispatcher is not None
    _OrchestratorFactory._remove_dispatcher()
    assert _OrchestratorFactory._dispatcher is None
