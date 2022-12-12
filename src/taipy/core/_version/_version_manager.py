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

from typing import List, Optional

from taipy.config import Config

from .._manager._manager import _Manager
from ..exceptions.exceptions import NonExistingVersion, VersionAlreadyExists
from ._version import _Version
from ._version_repository_factory import _VersionRepositoryFactory


class _VersionManager(_Manager[_Version]):
    _ENTITY_NAME = _Version.__name__

    __DEVELOPMENT_VERSION_NUMBER = ["development", "dev"]
    __CURRENT_VERSION_NUMBER = "current"
    __ALL_VERSION_NUMBER = ["all", ""]

    __DEFAULT_VERSION = __CURRENT_VERSION_NUMBER

    _repository = _VersionRepositoryFactory._build_repository()  # type: ignore

    @classmethod
    def get_or_create(cls, id: str, override: bool) -> _Version:
        if version := cls._get(id):
            if not override:
                raise VersionAlreadyExists(f"Version {id} already exists.")

            version.config = Config._applied_config
        else:
            version = _Version(id=id, config=Config._applied_config)

        cls._set(version)
        return version

    @classmethod
    def _get_all(cls, version_number: Optional[str] = "all") -> List[_Version]:
        """
        Returns all entities.
        """
        return cls._repository._load_all(version_number)

    @classmethod
    def _get_all_by(cls, by, version_number: Optional[str] = "all") -> List[_Version]:
        """
        Returns all entities based on a criteria.
        """
        return cls._repository._load_all_by(by, version_number)

    @classmethod
    def _set_current_version(cls, version_number: str, override: bool):
        cls.get_or_create(version_number, override)
        cls._repository._set_current_version(version_number)

    @classmethod
    def _get_current_version(cls) -> str:
        return cls._repository._get_current_version()

    @classmethod
    def _set_development_version(cls, version_number: str):
        cls.get_or_create(version_number, override=True)
        cls._repository._set_development_version(version_number)

    @classmethod
    def _get_development_version(cls) -> str:
        return cls._repository._get_development_version()

    @classmethod
    def _replace_version_number(cls, version_number):
        if version_number is None:
            version_number = cls.__DEFAULT_VERSION

        if version_number == cls.__CURRENT_VERSION_NUMBER:
            return cls._get_current_version()
        if version_number in cls.__DEVELOPMENT_VERSION_NUMBER:
            return cls._get_development_version()
        if version_number in cls.__ALL_VERSION_NUMBER:
            return ""
        if version := cls._get(version_number):
            return version.id

        raise NonExistingVersion(version_number)
