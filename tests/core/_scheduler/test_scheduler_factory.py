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

from unittest import mock

import pytest

from src.taipy.core._scheduler._dispatcher import _DevelopmentJobDispatcher, _JobDispatcher, _StandaloneJobDispatcher
from src.taipy.core._scheduler._scheduler import _Scheduler
from src.taipy.core._scheduler._scheduler_factory import _SchedulerFactory
from src.taipy.core.config.job_config import JobConfig
from src.taipy.core.exceptions.exceptions import SchedulerNotBuilt
from taipy.config import Config


def test_build_scheduler():
    _SchedulerFactory._scheduler = None
    _SchedulerFactory._dispatcher = None

    assert _SchedulerFactory._scheduler is None
    assert _SchedulerFactory._dispatcher is None

    scheduler = _SchedulerFactory._build_scheduler()
    assert scheduler == _Scheduler
    assert _SchedulerFactory._scheduler == _Scheduler
    dispatcher = _SchedulerFactory._build_dispatcher()
    assert isinstance(dispatcher, _JobDispatcher)
    assert isinstance(_SchedulerFactory._dispatcher, _JobDispatcher)

    _SchedulerFactory._scheduler = None
    assert _SchedulerFactory._scheduler is None
    assert _SchedulerFactory._dispatcher is not None

    with mock.patch(
        "src.taipy.core._scheduler._scheduler_factory._SchedulerFactory._build_dispatcher"
    ) as build_dispatcher, mock.patch("src.taipy.core._scheduler._scheduler._Scheduler.initialize") as initialize:
        scheduler = _SchedulerFactory._build_scheduler()
        assert scheduler == _Scheduler
        assert _SchedulerFactory._scheduler == _Scheduler
        build_dispatcher.assert_not_called()
        initialize.assert_called_once()


def test_build_development_dispatcher():
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE)
    _SchedulerFactory._scheduler = None
    _SchedulerFactory._dispatcher = None

    assert _SchedulerFactory._scheduler is None
    assert _SchedulerFactory._dispatcher is None

    with pytest.raises(SchedulerNotBuilt):
        _SchedulerFactory._build_dispatcher()

    _SchedulerFactory._build_scheduler()
    assert _SchedulerFactory._scheduler is not None
    assert _SchedulerFactory._dispatcher is None

    _SchedulerFactory._build_dispatcher()
    assert isinstance(_SchedulerFactory._dispatcher, _DevelopmentJobDispatcher)


def test_build_standalone_dispatcher():
    Config.configure_job_executions(mode=JobConfig._STANDALONE_MODE, max_nb_of_workers=2)
    _SchedulerFactory._build_dispatcher()
    assert isinstance(_SchedulerFactory._dispatcher, _StandaloneJobDispatcher)
    assert not isinstance(_SchedulerFactory._dispatcher, _DevelopmentJobDispatcher)
    assert _SchedulerFactory._dispatcher.is_running()
    assert _SchedulerFactory._dispatcher._nb_available_workers == 2
    _SchedulerFactory._dispatcher._nb_available_workers = 1

    _SchedulerFactory._build_dispatcher(force_restart=False)
    assert _SchedulerFactory._dispatcher.is_running()
    assert _SchedulerFactory._dispatcher._nb_available_workers == 1

    _SchedulerFactory._build_dispatcher(force_restart=True)
    assert _SchedulerFactory._dispatcher.is_running()
    assert _SchedulerFactory._dispatcher._nb_available_workers == 2
