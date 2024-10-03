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
import typing
from typing import Optional, Type

from taipy.common.config import Config

from ..common._check_dependencies import EnterpriseEditionUtils
from ..common._utils import _load_fct
from ..exceptions.exceptions import ModeNotAvailable, OrchestratorNotBuilt
from ._abstract_orchestrator import _AbstractOrchestrator
from ._dispatcher import _DevelopmentJobDispatcher, _JobDispatcher, _StandaloneJobDispatcher
from ._orchestrator import _Orchestrator


class _OrchestratorFactory:
    _TAIPY_ENTERPRISE_CORE_ORCHESTRATOR_MODULE = (
        EnterpriseEditionUtils._TAIPY_ENTERPRISE_MODULE + ".core._orchestrator._orchestrator"
    )
    _TAIPY_ENTERPRISE_CORE_DISPATCHER_MODULE = (
        EnterpriseEditionUtils._TAIPY_ENTERPRISE_MODULE + ".core._orchestrator._dispatcher"
    )
    __TAIPY_ENTERPRISE_BUILD_DISPATCHER_METHOD = "_build_dispatcher"

    _orchestrator: Optional[_AbstractOrchestrator] = None
    _dispatcher: Optional[_JobDispatcher] = None

    @classmethod
    def _build_orchestrator(cls) -> Type[_AbstractOrchestrator]:
        if cls._orchestrator:
            return cls._orchestrator  # type: ignore
        if EnterpriseEditionUtils._using_enterprise():
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

        if EnterpriseEditionUtils._using_enterprise():
            cls.__build_enterprise_job_dispatcher(force_restart=force_restart)
        elif Config.job_config.is_standalone:
            cls.__build_standalone_job_dispatcher(force_restart=force_restart)
        elif Config.job_config.is_development:
            cls.__build_development_job_dispatcher()
        else:
            raise ModeNotAvailable(f"Job mode {Config.job_config.mode} is not available.")

        return cls._dispatcher

    @classmethod
    def _remove_dispatcher(cls, wait: bool = True, timeout: Optional[float] = None) -> None:
        if cls._dispatcher is not None and not isinstance(cls._dispatcher, _DevelopmentJobDispatcher):
            cls._dispatcher.stop(wait, timeout)
        cls._dispatcher = None
        return cls._dispatcher

    @classmethod
    def __build_standalone_job_dispatcher(cls, force_restart=False):
        if isinstance(cls._dispatcher, _StandaloneJobDispatcher):
            if force_restart:
                cls._dispatcher.stop()
            else:
                return

        if EnterpriseEditionUtils._using_enterprise():
            cls._dispatcher = _load_fct(
                cls._TAIPY_ENTERPRISE_CORE_DISPATCHER_MODULE, cls.__TAIPY_ENTERPRISE_BUILD_DISPATCHER_METHOD
            )(cls._orchestrator)
        else:
            cls._dispatcher = _StandaloneJobDispatcher(typing.cast(_AbstractOrchestrator, cls._orchestrator))
        cls._dispatcher.start()  # type: ignore

    @classmethod
    def __build_development_job_dispatcher(cls):
        if isinstance(cls._dispatcher, _StandaloneJobDispatcher):
            cls._dispatcher.stop()

        if EnterpriseEditionUtils._using_enterprise():
            cls._dispatcher = _load_fct(
                cls._TAIPY_ENTERPRISE_CORE_DISPATCHER_MODULE, cls.__TAIPY_ENTERPRISE_BUILD_DISPATCHER_METHOD
            )(cls._orchestrator)
        else:
            cls._dispatcher = _DevelopmentJobDispatcher(typing.cast(_AbstractOrchestrator, cls._orchestrator))

    @classmethod
    def __build_enterprise_job_dispatcher(cls, force_restart=False):
        cls._dispatcher = _load_fct(
            cls._TAIPY_ENTERPRISE_CORE_DISPATCHER_MODULE, cls.__TAIPY_ENTERPRISE_BUILD_DISPATCHER_METHOD
        )(typing.cast(_AbstractOrchestrator, cls._orchestrator), force_restart)
        if cls._dispatcher:
            cls._dispatcher.start()
        else:
            raise ModeNotAvailable(f"Job mode {Config.job_config.mode} is not available.")
