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

from importlib import util
from typing import Optional, Type

from taipy.config.config import Config

from ..common._utils import _load_fct
from ..exceptions.exceptions import ModeNotAvailable, OrchestratorNotBuilt
from ._abstract_orchestrator import _AbstractOrchestrator
from ._dispatcher import _DevelopmentJobDispatcher, _JobDispatcher, _StandaloneJobDispatcher
from ._orchestrator import _Orchestrator


class _OrchestratorFactory:
    _TAIPY_ENTERPRISE_MODULE = "taipy.enterprise"
    _TAIPY_ENTERPRISE_CORE_ORCHESTRATOR_MODULE = _TAIPY_ENTERPRISE_MODULE + ".core._orchestrator._orchestrator"
    _TAIPY_ENTERPRISE_CORE_DISPATCHER_MODULE = _TAIPY_ENTERPRISE_MODULE + ".core._orchestrator._dispatcher"
    __STANDADLONE_JOB_DISPATCHER_TYPE = "_StandaloneJobDispatcher"

    _orchestrator: Optional[_Orchestrator] = None
    _dispatcher: Optional[_JobDispatcher] = None

    @classmethod
    def _build_orchestrator(cls) -> Type[_AbstractOrchestrator]:
        if util.find_spec(cls._TAIPY_ENTERPRISE_MODULE) is not None:
            cls._orchestrator = _load_fct(
                cls._TAIPY_ENTERPRISE_CORE_ORCHESTRATOR_MODULE,
                "Orchestrator",
            )  # type: ignore
        else:
            cls._orchestrator = _Orchestrator  # type: ignore

        cls._orchestrator.initialize()  # type: ignore

        return cls._orchestrator  # type: ignore

    @classmethod
    def _build_dispatcher(cls, force_restart=False) -> Optional[_JobDispatcher]:
        if not cls._orchestrator:
            raise OrchestratorNotBuilt
        if Config.job_config.is_standalone:
            return cls.__build_standalone_job_dispatcher(force_restart=force_restart)
        elif Config.job_config.is_development:
            return cls.__build_development_job_dispatcher()
        else:
            raise ModeNotAvailable(f"Job mode {Config.job_config.mode} is not available.")

    @classmethod
    def _remove_dispatcher(cls) -> Optional[_JobDispatcher]:
        if isinstance(cls._dispatcher, _StandaloneJobDispatcher) and not isinstance(
            cls._dispatcher, _DevelopmentJobDispatcher
        ):
            cls._dispatcher.stop()

        cls._dispatcher = None

        return cls._dispatcher

    @classmethod
    def __build_standalone_job_dispatcher(cls, force_restart=False) -> Optional[_JobDispatcher]:
        if isinstance(cls._dispatcher, _StandaloneJobDispatcher) and not isinstance(
            cls._dispatcher, _DevelopmentJobDispatcher
        ):
            if force_restart:
                cls._dispatcher.stop()
            else:
                return None

        if util.find_spec(cls._TAIPY_ENTERPRISE_MODULE) is not None:
            cls._dispatcher = _load_fct(
                cls._TAIPY_ENTERPRISE_CORE_DISPATCHER_MODULE, cls.__STANDADLONE_JOB_DISPATCHER_TYPE
            )(cls._orchestrator)
        else:
            cls._dispatcher = _StandaloneJobDispatcher(cls._orchestrator)  # type: ignore

        cls._dispatcher.start()  # type: ignore
        return cls._dispatcher

    @classmethod
    def __build_development_job_dispatcher(cls) -> _JobDispatcher:
        if isinstance(cls._dispatcher, _StandaloneJobDispatcher) and not isinstance(
            cls._dispatcher, _DevelopmentJobDispatcher
        ):
            cls._dispatcher.stop()
        cls._dispatcher = _DevelopmentJobDispatcher(cls._orchestrator)  # type: ignore
        return cls._dispatcher
