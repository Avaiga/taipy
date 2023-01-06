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

import json
from datetime import datetime
from typing import List, Optional

from taipy.config import Config
from taipy.logger._taipy_logger import _TaipyLogger

from .._repository._sql_repository import _SQLVersionBaseRepository
from ..exceptions.exceptions import VersionIsNotProductionVersion
from ._version import _Version
from ._version_model import _VersionModel


class _VersionSQLRepository(_SQLVersionBaseRepository):
    _LATEST_VERSION_KEY = "latest_version"
    _DEVELOPMENT_VERSION_KEY = "development_version"
    _PRODUCTION_VERSION_KEY = "production_version"

    def __init__(self):
        super().__init__(_VersionModel, self._to_model, self._from_model)

    def _to_model(self, version: _Version):
        return _VersionModel(
            id=version.id, config=Config._to_json(version.config), creation_date=version.creation_date.isoformat()
        )

    def _from_model(self, model):
        version = _Version(id=model.id, config=Config._from_json(model.config))
        version.creation_date = datetime.fromisoformat(model.creation_date)
        return version

    def _load_all_by(self, by, version_number: Optional[str] = "all"):
        return super()._load_all_by(by, version_number)

    def _set_latest_version(self, version_number):
        version = self.load(version_number)
        version.is_latest = True

        if old_latest := self.session.query(self._table).filter_by(is_latest=True).first():
            old_latest.is_latest = False
        self.session.commit()

    def _get_latest_version(self):
        if latest := self.session.query(self._table).filter_by(is_latest=True).first():
            return latest.id
        return ""

    def _set_development_version(self, version_number):
        version = self.load(version_number)
        version.is_development = True

        if old_development := self.session.query(self._table).filter_by(is_development=True).first():
            old_development.is_development = False

        self._set_latest_version(version_number)

        self.session.commit()

    def _get_development_version(self):
        if development := self.session.query(self._table).filter_by(is_development=True).first():
            return development.id
        return ""

    def _set_production_version(self, version_number):
        version = self.load(version_number)
        version.is_production = True

        self._set_latest_version(version_number)

        self.session.commit()

    def _get_production_version(self):
        if productions := self.session.query(self._table).filter_by(is_production=True).all():
            return [p.id for p in productions]
        return []

    def _delete_production_version(self, version_number):
        version = self.load(version_number)
        version.is_production = False

        self.session.commit()
