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

from sqlalchemy.dialects import sqlite

from .._repository._sql_repository import _SQLRepository
from ..exceptions.exceptions import ModelNotFound, VersionIsNotProductionVersion
from ._version_converter import _VersionConverter
from ._version_model import _VersionModel
from ._version_repository_interface import _VersionRepositoryInterface


class _VersionSQLRepository(_SQLRepository, _VersionRepositoryInterface):
    def __init__(self) -> None:
        super().__init__(model_type=_VersionModel, converter=_VersionConverter)

    def _set_latest_version(self, version_number):
        if old_latest := self.db.execute(str(self.table.select().filter_by(is_latest=True))).fetchone():
            old_latest = self.model_type.from_dict(old_latest)
            old_latest.is_latest = False
            self._update_entry(old_latest)

        version = self.__get_by_id(version_number)
        version.is_latest = True
        self._update_entry(version)

    def _get_latest_version(self):
        if latest := self.db.execute(
            str(self.table.select().filter_by(is_latest=True).compile(dialect=sqlite.dialect()))
        ).fetchone():
            return latest["id"]
        raise ModelNotFound(self.model_type, "")

    def _set_development_version(self, version_number):
        if old_development := self.db.execute(str(self.table.select().filter_by(is_development=True))).fetchone():
            old_development = self.model_type.from_dict(old_development)
            old_development.is_development = False
            self._update_entry(old_development)

        version = self.__get_by_id(version_number)
        version.is_development = True
        self._update_entry(version)

        self._set_latest_version(version_number)

    def _get_development_version(self):
        if development := self.db.execute(str(self.table.select().filter_by(is_development=True))).fetchone():
            return development["id"]
        raise ModelNotFound(self.model_type, "")

    def _set_production_version(self, version_number):
        version = self.__get_by_id(version_number)
        version.is_production = True
        self._update_entry(version)

        self._set_latest_version(version_number)

    def _get_production_versions(self):
        if productions := self.db.execute(
            str(self.table.select().filter_by(is_production=True).compile(dialect=sqlite.dialect())),
        ).fetchall():
            return [p["id"] for p in productions]
        return []

    def _delete_production_version(self, version_number):
        version = self.__get_by_id(version_number)

        if not version or not version.is_production:
            raise VersionIsNotProductionVersion(f"Version '{version_number}' is not a production version.")
        version.is_production = False
        self._update_entry(version)

    def __get_by_id(self, version_id):
        query = str(self.table.select().filter_by(id=version_id).compile(dialect=sqlite.dialect()))
        entry = self.db.execute(query, [version_id]).fetchone()
        return self.model_type.from_dict(entry) if entry else None
