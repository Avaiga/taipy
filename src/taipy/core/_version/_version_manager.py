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

from taipy.config import Config

from .._manager._manager import _Manager
from ..exceptions.exceptions import VersionAlreadyExists
from ._version import _Version
from ._version_repository_factory import _VersionRepositoryFactory


class _VersionManager(_Manager[_Version]):
    _ENTITY_NAME = _Version.__name__

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
    def set_current_version(cls, version_number: str, override: bool):
        cls.get_or_create(version_number, override)
        cls._repository._set_current_version(version_number)

    @classmethod
    def get_current_version(cls) -> str:
        return cls._repository._get_current_version()

    @classmethod
    def set_development_version(cls, version_number: str):
        cls.get_or_create(version_number, override=True)
        cls._repository._set_development_version(version_number)

    @classmethod
    def get_development_version(cls) -> str:
        return cls._repository._get_development_version()
