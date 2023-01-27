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

import uuid
from typing import Optional

from taipy.config import Config
from taipy.logger._taipy_logger import _TaipyLogger

from ._scheduler._dispatcher._job_dispatcher import _JobDispatcher
from ._scheduler._scheduler import _Scheduler
from ._scheduler._scheduler_factory import _SchedulerFactory
from ._version._version_cli import _VersioningCLI
from ._version._version_manager_factory import _VersionManagerFactory
from .exceptions.exceptions import VersionConflictWithPythonConfig
from .taipy import clean_all_entities_by_version


class Core:
    """
    Core service
    """

    _scheduler: Optional[_Scheduler] = None
    _dispatcher: Optional[_JobDispatcher] = None

    def __init__(self):
        """
        Initialize a Core service.
        """
        _VersioningCLI._create_parser()
        self.cli_args = _VersioningCLI._parse_arguments()
        self._scheduler = _SchedulerFactory._build_scheduler()

    def run(self, force_restart=False):
        """
        Start a Core service.

        This function check the configuration, start a dispatcher and lock the Config.
        """
        self.__check_config()
        self.__manage_version(*self.cli_args)
        self.__start_dispatcher(force_restart)

    def stop(self):
        """
        Stop the Core service.

        This function stops the dispatcher and unblock the Config for update.
        """
        Config.unblock_update()

        if self._dispatcher:
            self._dispatcher = _SchedulerFactory._remove_dispatcher()
            _TaipyLogger._get_logger().info("Core service has been stopped.")

    def __check_config(self):
        Config.check()
        Config.block_update()

    def __manage_version(self, mode, _version_number, force, clean_entities):
        if mode == "development":
            current_version_number = _VersionManagerFactory._build_manager()._get_development_version()

            clean_all_entities_by_version(current_version_number)
            _TaipyLogger._get_logger().info(f"Development mode: Clean all entities of version {current_version_number}")

            _VersionManagerFactory._build_manager()._set_development_version(current_version_number)

        elif mode in ["experiment", "production"]:
            default_version_number = {
                "experiment": str(uuid.uuid4()),
                "production": _VersionManagerFactory._build_manager()._get_latest_version(),
            }

            version_setter = {
                "experiment": _VersionManagerFactory._build_manager()._set_experiment_version,
                "production": _VersionManagerFactory._build_manager()._set_production_version,
            }

            if _version_number:
                current_version_number = _version_number
            else:
                current_version_number = default_version_number[mode]

            if clean_entities:
                clean_all_entities_by_version(current_version_number)
                _TaipyLogger._get_logger().info(f"Clean all entities of version {current_version_number}")

            try:
                version_setter[mode](current_version_number, force)
            except VersionConflictWithPythonConfig as e:
                raise SystemExit(e.message)

        else:
            raise SystemExit(f"Undefined execution mode: {mode}.")

    def __start_dispatcher(self, force_restart):
        if dispatcher := _SchedulerFactory._build_dispatcher(force_restart=force_restart):
            self._dispatcher = dispatcher

        if Config.job_config.is_development:
            _Scheduler._check_and_execute_jobs_if_development_mode()
