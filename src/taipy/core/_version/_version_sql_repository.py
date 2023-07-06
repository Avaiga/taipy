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

from .._repository._sql_repository import _SQLRepository
from ..exceptions.exceptions import ModelNotFound, VersionIsNotProductionVersion
from ._version_converter import _VersionConverter
from ._version_model import _VersionModel
from ._version_repository_interface import _VersionRepositoryInterface


class _VersionSQLRepository(_SQLRepository, _VersionRepositoryInterface):
    def __init__(self):
        super().__init__(model_type=_VersionModel, converter=_VersionConverter)

    def _set_latest_version(self, version_number):
        if old_latest := self.db.query(self.model_type).filter_by(is_latest=True).first():
            old_latest.is_latest = False

        version = self.__get_by_id(version_number)
        version.is_latest = True

        self.db.commit()

    def _get_latest_version(self):
        if latest := self.db.query(self.model_type).filter_by(is_latest=True).first():
            return latest.id
        return ""

    def _set_development_version(self, version_number):
        if old_development := self.db.query(self.model_type).filter_by(is_development=True).first():
            old_development.is_development = False

        version = self.__get_by_id(version_number)
        version.is_development = True

        self._set_latest_version(version_number)

        self.db.commit()

    def _get_development_version(self):
        if development := self.db.query(self.model_type).filter_by(is_development=True).first():
            return development.id
        raise ModelNotFound(self.model_type, "")

    def _set_production_version(self, version_number):
        version = self.__get_by_id(version_number)
        version.is_production = True

        self._set_latest_version(version_number)

        self.db.commit()

    def _get_production_versions(self):
        if productions := self.db.query(self.model_type).filter_by(is_production=True).all():
            return [p.id for p in productions]
        return []

    def _delete_production_version(self, version_number):
        version = self.__get_by_id(version_number)

        if not version or not version.is_production:
            raise VersionIsNotProductionVersion(f"Version '{version_number}' is not a production version.")
        version.is_production = False

        self.db.commit()

    def __get_by_id(self, version_id):
        return self.db.query(self.model_type).filter_by(id=version_id).first()
