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
from typing import List, Optional, Union

from taipy.config import Config
from taipy.config._config_comparator._comparator_result import _ComparatorResult
from taipy.config.checker.issue_collector import IssueCollector
from taipy.config.exceptions.exceptions import InconsistentEnvVariableError
from taipy.logger._taipy_logger import _TaipyLogger

from .._manager._manager import _Manager
from ..exceptions.exceptions import ConflictedConfigurationError, ModelNotFound, NonExistingVersion
from ._version import _Version
from ._version_fs_repository import _VersionFSRepository


class _VersionManager(_Manager[_Version]):
    _ENTITY_NAME = _Version.__name__

    __logger = _TaipyLogger._get_logger()

    __DEVELOPMENT_VERSION = ["development", "dev"]
    __LATEST_VERSION = "latest"
    __PRODUCTION_VERSION = "production"
    __ALL_VERSION = ["all", ""]

    _DEFAULT_VERSION = __LATEST_VERSION

    _repository: _VersionFSRepository

    @classmethod
    def _get(cls, entity: Union[str, _Version], default=None) -> _Version:
        """
        Returns the version entity by id or reference.
        """
        entity_id = entity if isinstance(entity, str) else entity.id
        try:
            return cls._repository._load(entity_id)
        except ModelNotFound:
            return default

    @classmethod
    def _get_or_create(cls, id: str, force: bool) -> _Version:
        if version := cls._get(id):
            comparator_result = Config._comparator._find_conflict_config(version.config, Config._applied_config, id)
            if comparator_result.get(_ComparatorResult.CONFLICTED_SECTION_KEY):
                if force:
                    cls.__logger.warning(
                        f"Option --force is detected, overriding the configuration of version {id} ..."
                    )
                    version.config = Config._applied_config
                else:
                    raise ConflictedConfigurationError()

        else:
            version = _Version(id=id, config=Config._applied_config)

        cls._set(version)
        return version

    @classmethod
    def _get_all(cls, version_number: Optional[Union[str, List]] = "all") -> List[_Version]:
        """
        Returns all entities.
        """
        version_number = cls._replace_version_number(version_number)  # type: ignore
        if not isinstance(version_number, List):
            version_number = [version_number] if version_number else []
        filters = [{"version": version} for version in version_number]
        return cls._repository._load_all(filters)

    @classmethod
    def _set_development_version(cls, version_number: str) -> str:
        cls._get_or_create(version_number, force=True)
        cls._repository._set_development_version(version_number)
        return version_number

    @classmethod
    def _get_development_version(cls) -> str:
        try:
            return cls._repository._get_development_version()
        except (FileNotFoundError, ModelNotFound):
            return cls._set_development_version(str(uuid.uuid4()))

    @classmethod
    def _set_experiment_version(cls, version_number: str, force: bool = False) -> str:
        if version_number == cls._get_development_version():
            raise SystemExit(
                f"Version number {version_number} is the development version. Please choose a different name"
                f" for this experiment."
            )

        if version_number in cls._get_production_versions():
            raise SystemExit(
                f"Version number {version_number} is already a production version. Please choose a different name"
                f" for this experiment."
            )

        try:
            cls._get_or_create(version_number, force)
        except ConflictedConfigurationError:
            raise SystemExit(
                f"Please add a new experiment version or run your application with --force option to"
                f" override the Config of experiment {version_number}."
            )
        cls._repository._set_latest_version(version_number)
        return version_number

    @classmethod
    def _get_latest_version(cls) -> str:
        try:
            return cls._repository._get_latest_version()
        except (FileNotFoundError, ModelNotFound):
            # If there is no version in the system yet, create a new version as development version
            # This set the default versioning behavior on Jupyter notebook to Development mode
            return cls._set_development_version(str(uuid.uuid4()))

    @classmethod
    def _set_production_version(cls, version_number: str, force: bool = False) -> str:
        if version_number == cls._get_development_version():
            cls._set_development_version(str(uuid.uuid4()))

        try:
            cls._get_or_create(version_number, force)
        except ConflictedConfigurationError:
            raise SystemExit(
                f"Please add a new production version with migration functions.\n"
                f"If old entities remain compatible with the new configuration, you can also run your application with"
                f" --force option to override the production configuration of version {version_number}."
            )
        cls._repository._set_production_version(version_number)
        return version_number

    @classmethod
    def _get_production_versions(cls) -> List[str]:
        try:
            return cls._repository._get_production_versions()
        except (FileNotFoundError, ModelNotFound):
            return []

    @classmethod
    def _delete_production_version(cls, version_number) -> str:
        return cls._repository._delete_production_version(version_number)

    @classmethod
    def _replace_version_number(cls, version_number: Optional[str] = None):
        if version_number is None:
            version_number = cls._replace_version_number(cls._DEFAULT_VERSION)

            production_versions = cls._get_production_versions()
            if version_number in production_versions:
                return production_versions

            return version_number

        if version_number == cls.__LATEST_VERSION:
            return cls._get_latest_version()
        if version_number in cls.__DEVELOPMENT_VERSION:
            return cls._get_development_version()
        if version_number == cls.__PRODUCTION_VERSION:
            return cls._get_production_versions()
        if version_number in cls.__ALL_VERSION:
            return ""

        try:
            if version := cls._get(version_number):
                return version.id
        except InconsistentEnvVariableError:  # The version exist but the Config is alternated
            return version_number

        raise NonExistingVersion(version_number)

    @classmethod
    def _manage_version(cls):
        from ..taipy import clean_all_entities_by_version

        if Config.core.mode == "development":
            current_version_number = cls._get_development_version()
            cls.__logger.info(f"Development mode: Clean all entities of version {current_version_number}")
            clean_all_entities_by_version(current_version_number)
            cls._set_development_version(current_version_number)

        elif Config.core.mode in ["experiment", "production"]:
            default_version_number = {
                "experiment": str(uuid.uuid4()),
                "production": cls._get_latest_version(),
            }
            version_setter = {
                "experiment": cls._set_experiment_version,
                "production": cls._set_production_version,
            }

            if Config.core.version_number:
                current_version_number = Config.core.version_number
            else:
                current_version_number = default_version_number[Config.core.mode]

            version_setter[Config.core.mode](current_version_number, Config.core.force)
            if Config.core.mode == "production":
                cls.__check_production_migration_config()
        else:
            raise SystemExit(f"Undefined execution mode: {Config.core.mode}.")

    @classmethod
    def __check_production_migration_config(self):
        from ..config.checkers._migration_config_checker import _MigrationConfigChecker

        collector = _MigrationConfigChecker(Config._applied_config, IssueCollector())._check()
        for issue in collector._warnings:
            self.__logger.warning(str(issue))
        for issue in collector._infos:
            self.__logger.info(str(issue))
        for issue in collector._errors:
            self.__logger.error(str(issue))
        if len(collector._errors) != 0:
            raise SystemExit("Configuration errors found. Please check the error log for more information.")

    @classmethod
    def _delete_entities_of_multiple_types(cls, _entity_ids):
        return NotImplementedError
