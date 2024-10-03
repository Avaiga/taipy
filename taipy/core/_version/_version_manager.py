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

import uuid
from typing import List, Optional, Union

from taipy.common.config import Config
from taipy.common.config._config_comparator._comparator_result import _ComparatorResult
from taipy.common.config.exceptions.exceptions import InconsistentEnvVariableError
from taipy.common.logger._taipy_logger import _TaipyLogger

from .._manager._manager import _Manager
from ..exceptions.exceptions import (
    ConfigCoreVersionMismatched,
    ConflictedConfigurationError,
    ModelNotFound,
    NonExistingVersion,
    VersionAlreadyExistsAsDevelopment,
)
from ..reason import ReasonCollection
from ._version import _Version
from ._version_fs_repository import _VersionFSRepository


class _VersionManager(_Manager[_Version]):
    _ENTITY_NAME = _Version.__name__

    _logger = _TaipyLogger._get_logger()

    _DEVELOPMENT_VERSION = ["development", "dev"]
    _LATEST_VERSION = "latest"
    _ALL_VERSION = ["all", ""]

    _DEFAULT_VERSION = _LATEST_VERSION

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
            comparator_result = Config._comparator._find_conflict_config(version.config, Config._applied_config, id)  # type: ignore[attr-defined]
            if comparator_result.get(_ComparatorResult.CONFLICTED_SECTION_KEY):
                if not force:
                    raise ConflictedConfigurationError()

                cls._logger.warning(f"Option --force is detected, overriding the configuration of version {id} ...")
                version.config = Config._applied_config  # type: ignore[attr-defined]

        else:
            version = _Version(id=id, config=Config._applied_config)  # type: ignore[attr-defined]

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
    def _is_deletable(cls, version_number: Optional[str]) -> ReasonCollection:
        return ReasonCollection()

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
            raise VersionAlreadyExistsAsDevelopment(version_number)

        try:
            cls._get_or_create(version_number, force)
        except ConflictedConfigurationError:
            raise SystemExit(
                f"Please add a new experiment version or run your application with --force option to"
                f" override the Config of experiment {version_number}."
            ) from None
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
    def _replace_version_number(cls, version_number: Optional[str] = None):
        if version_number is None:
            return cls._replace_version_number(cls._DEFAULT_VERSION)

        if version_number == cls._LATEST_VERSION:
            return cls._get_latest_version()
        if version_number in cls._DEVELOPMENT_VERSION:
            return cls._get_development_version()
        if version_number in cls._ALL_VERSION:
            return ""

        try:
            if version := cls._get(version_number):
                return version.id
        except InconsistentEnvVariableError:  # The version exist but the Config is alternated
            return version_number
        except ConfigCoreVersionMismatched as e:
            cls._logger.error(e.message)
            raise SystemExit() from e

        raise NonExistingVersion(version_number)

    @classmethod
    def _rename_version(cls, old_version: str, new_version: str) -> None:
        version_entity = cls._get(old_version)

        if old_version == cls._get_latest_version():
            try:
                cls._set_experiment_version(new_version)
            except VersionAlreadyExistsAsDevelopment as err:
                raise SystemExit(err.message) from None
        if old_version == cls._get_development_version():
            cls._set_development_version(new_version)
        cls._delete(old_version)

        if not cls._get(new_version):
            version_entity.id = new_version
            cls._set(version_entity)

    @classmethod
    def _manage_version(cls) -> None:
        if Config.core.mode == "development":
            from ..taipy import clean_all_entities

            current_version_number = cls._get_development_version()
            cls._logger.info(f"Development mode: Clean all entities of version {current_version_number}")
            clean_all_entities(current_version_number)
            cls._set_development_version(current_version_number)

        elif Config.core.mode == "experiment":
            if Config.core.version_number:
                current_version_number = Config.core.version_number
            else:
                current_version_number = str(uuid.uuid4())

            try:
                cls._set_experiment_version(current_version_number, Config.core.force)
            except VersionAlreadyExistsAsDevelopment as err:
                raise SystemExit(err.message) from None

        else:
            raise SystemExit(f"Undefined execution mode: {Config.core.mode}.")

    @classmethod
    def _delete_entities_of_multiple_types(cls, _entity_ids):
        raise NotImplementedError
