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
from importlib import util
from typing import Type

from taipy.config.config import Config
from taipy.config.exceptions.exceptions import ModeNotAvailable

from ..common._utils import _load_fct
from ..exceptions.exceptions import SchedulerNotBuilt
from ._abstract_scheduler import _AbstractScheduler
from ._dispatcher import _DevelopmentJobDispatcher, _JobDispatcher, _StandaloneJobDispatcher
from ._scheduler import _Scheduler


class _SchedulerFactory:

    _TAIPY_ENTERPRISE_MODULE = "taipy.enterprise"
    _TAIPY_ENTERPRISE_CORE_MODULE = _TAIPY_ENTERPRISE_MODULE + ".core._scheduler._scheduler"
    _dispatcher = None
    _scheduler = None

    @classmethod
    def _build_scheduler(cls) -> Type[_AbstractScheduler]:
        # Build scheduler
        if util.find_spec(cls._TAIPY_ENTERPRISE_MODULE) is not None:
            cls._scheduler = _load_fct(
                cls._TAIPY_ENTERPRISE_CORE_MODULE,
                "Scheduler",
            )
        else:
            cls._scheduler = _Scheduler

        if not cls._dispatcher:
            cls._build_dispatcher()

        cls._scheduler.initialize()  # type: ignore

        return cls._scheduler  # type: ignore

    @classmethod
    def _update_job_config(cls, force_restart=False):
        cls._build_dispatcher(force_restart=force_restart)

    @classmethod
    def _build_dispatcher(cls, force_restart=False):
        if not cls._scheduler:
            raise SchedulerNotBuilt

        if Config.job_config.is_standalone:
            cls.__build_standalone_job_dispatcher(force_restart=force_restart)
        elif Config.job_config.is_development:
            cls.__build_development_job_dispatcher()
        else:
            raise ModeNotAvailable

    @classmethod
    def __build_standalone_job_dispatcher(cls, force_restart=False):
        if isinstance(cls._dispatcher, _StandaloneJobDispatcher) and not isinstance(
            cls._dispatcher, _DevelopmentJobDispatcher
        ):
            if force_restart:
                cls._dispatcher.stop()
            else:
                return
        cls._dispatcher = _StandaloneJobDispatcher(cls._scheduler)
        cls._dispatcher.start()

    @classmethod
    def __build_development_job_dispatcher(cls):
        if isinstance(cls._dispatcher, _StandaloneJobDispatcher) and not isinstance(
            cls._dispatcher, _DevelopmentJobDispatcher
        ):
            cls._dispatcher.stop()
        cls._dispatcher = _DevelopmentJobDispatcher(cls._scheduler)

    @classmethod
    def _get_dispatcher(cls) -> _JobDispatcher:
        if not cls._scheduler:
            cls._build_scheduler()
        elif not cls._dispatcher:
            cls._build_dispatcher()
        return cls._dispatcher  # type: ignore
