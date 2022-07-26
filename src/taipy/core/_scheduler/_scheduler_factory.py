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
from ._abstract_scheduler import _AbstractScheduler
from ._scheduler import _Scheduler


class _SchedulerFactory:

    _TAIPY_ENTERPRISE_MODULE = "taipy.enterprise"
    _TAIPY_ENTERPRISE_CORE_MODULE = _TAIPY_ENTERPRISE_MODULE + ".core._scheduler._scheduler"
    _dispatcher = None

    @classmethod
    def _build_scheduler(cls) -> Type[_AbstractScheduler]:
        if Config.job_config.is_standalone or Config.job_config.is_development:
            if util.find_spec(cls._TAIPY_ENTERPRISE_MODULE) is not None:
                scheduler = _load_fct(
                    cls._TAIPY_ENTERPRISE_CORE_MODULE,
                    "Scheduler",
                )
            else:
                scheduler = _Scheduler
            if cls._dispatcher is None:
                # If dispatcher mode is standalone => load dispatcher and run thread, if not, don't load dispatcher
                # Get the correct _StandaloneJobDispatcher or _DevelopmentJobDispatcher
                from ._dispatcher._standalone_job_dispatcher import _StandaloneJobDispatcher

                cls._dispatcher = _StandaloneJobDispatcher(
                    scheduler
                )  # TODO: this should be _StandaloneJobDispatcher or _DevelopmentJobDispatcher
                cls._dispatcher.start()

        else:
            raise ModeNotAvailable
        scheduler.initialize()  # type: ignore
        return scheduler  # type: ignore

    # @classmethod
    # def _update_job_config(cls):
    #     if Config.job_config.is_standalone:  # type: ignore
    #         from ._dispatcher._standalone_job_dispatcher import _StandaloneJobDispatcher
    #         cls._dispatcher = _StandaloneJobDispatcher() # TODO: pass in the scheduler
    #         cls._dispatcher.start()
    #     else:
    #         from ._dispatcher._development_job_dispatcher import _DevelopmentJobDispatcher
    #         cls._dispatcher = _DevelopmentJobDispatcher()
