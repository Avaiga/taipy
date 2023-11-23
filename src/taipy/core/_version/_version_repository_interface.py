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

from abc import ABC, abstractmethod


class _VersionRepositoryInterface(ABC):
    _LATEST_VERSION_KEY = "latest_version"
    _DEVELOPMENT_VERSION_KEY = "development_version"
    _PRODUCTION_VERSION_KEY = "production_version"

    @abstractmethod
    def _set_latest_version(self, version_number):
        raise NotImplementedError

    @abstractmethod
    def _get_latest_version(self):
        raise NotImplementedError

    @abstractmethod
    def _set_development_version(self, version_number):
        raise NotImplementedError

    @abstractmethod
    def _get_development_version(self):
        raise NotImplementedError

    @abstractmethod
    def _set_production_version(self, version_number):
        raise NotImplementedError

    @abstractmethod
    def _get_production_versions(self):
        raise NotImplementedError

    @abstractmethod
    def _delete_production_version(self, version_number):
        raise NotImplementedError
