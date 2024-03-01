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

from multiprocessing import Lock
from typing import Optional

from taipy.config import Config
from taipy.logger._taipy_logger import _TaipyLogger

from ._backup._backup import _init_backup_file_with_storage_folder
from ._core_cli import _CoreCLI
from ._orchestrator._dispatcher._job_dispatcher import _JobDispatcher
from ._orchestrator._orchestrator import _Orchestrator
from ._orchestrator._orchestrator_factory import _OrchestratorFactory
from ._version._version_manager_factory import _VersionManagerFactory
from .config import CoreSection
from .exceptions.exceptions import CoreServiceIsAlreadyRunning


class Core:
    """
    Core service
    """

    _is_running = False
    __lock_is_running = Lock()

    _version_is_initialized = False
    __lock_version_is_initialized = Lock()

    __logger = _TaipyLogger._get_logger()

    _orchestrator: Optional[_Orchestrator] = None
    _dispatcher: Optional[_JobDispatcher] = None

    def __init__(self):
        """
        Initialize a Core service.
        """
        pass

    def run(self, force_restart=False):
        """
        Start a Core service.

        This function checks and locks the configuration, manages application's version,
        and starts a job dispatcher.
        """
        if self.__class__._is_running:
            raise CoreServiceIsAlreadyRunning

        with self.__class__.__lock_is_running:
            self.__class__._is_running = True

        self._manage_version_and_block_config()
        self.__start_dispatcher(force_restart)

    def stop(self, wait: bool = True, timeout: Optional[float] = None):
        """
        Stop the Core service.
        This function stops the dispatcher and unblock the Config for update.

        Parameters:
            wait (bool): If True, the method will wait for the dispatcher to stop.
            timeout (Optional[float]): The maximum time to wait. If None, the method will wait indefinitely.
        """
        self.__logger.info("Unblocking configuration update.")
        Config.unblock_update()

        if self._dispatcher:
            self._dispatcher = _OrchestratorFactory._remove_dispatcher(wait, timeout)
            self.__logger.info("Core service has been stopped.")

        with self.__class__.__lock_is_running:
            self.__class__._is_running = False

        with self.__class__.__lock_version_is_initialized:
            self.__class__._version_is_initialized = False

    @classmethod
    def _manage_version_and_block_config(cls):
        """
        Manage the application's version and block the Config from updates.
        """
        if cls._version_is_initialized:
            return

        with cls.__lock_version_is_initialized:
            cls._version_is_initialized = True

        cls.__update_core_section()
        cls.__manage_version()
        cls.__check_and_block_config()

    @classmethod
    def __update_core_section(cls):
        _CoreCLI.create_parser()
        Config._applied_config._unique_sections[CoreSection.name]._update(_CoreCLI.parse_arguments())

    @classmethod
    def __manage_version(cls):
        _VersionManagerFactory._build_manager()._manage_version()
        Config._applied_config._unique_sections[CoreSection.name]._update(
            {"version_number": _VersionManagerFactory._build_manager()._get_latest_version()}
        )

    @classmethod
    def __check_and_block_config(cls):
        Config.check()
        cls.__logger.info("Blocking configuration update.")
        Config.block_update()
        _init_backup_file_with_storage_folder()

    def __start_dispatcher(self, force_restart):
        if self._orchestrator is None:
            self._orchestrator = _OrchestratorFactory._build_orchestrator()

        if dispatcher := _OrchestratorFactory._build_dispatcher(force_restart=force_restart):
            self._dispatcher = dispatcher

        if Config.job_config.is_development:
            _Orchestrator._check_and_execute_jobs_if_development_mode()
