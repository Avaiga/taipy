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

import pytest

from src.taipy.core._repository import _sql_repository
from src.taipy.core._version._version import _Version
from src.taipy.core._version._version_sql_repository import _VersionSQLRepository
from src.taipy.core.exceptions import VersionIsNotProductionVersion
from taipy.config.config import Config


class TestVersionSQLRepository:
    def test_save_and_load(self, mocker, sql_engine):
        Config.global_config.repository_type = "sql"
        mocker.patch.object(_sql_repository, "create_engine", return_value=sql_engine)
        repo = _VersionSQLRepository()
        expected = _Version(id="foo", config=Config._applied_config)
        repo._save(expected)

        assert expected == repo.load("foo")

    def test_load_all(self, mocker, sql_engine):
        Config.global_config.repository_type = "sql"
        mocker.patch.object(_sql_repository, "create_engine", return_value=sql_engine)
        repo = _VersionSQLRepository()

        assert len(repo._load_all()) == 0

        version = _Version(id="foo", config=Config._applied_config)
        repo._save(version)

        assert len(repo._load_all()) == 1

    def test_get_set_latest_version(self, mocker, sql_engine):
        Config.global_config.repository_type = "sql"
        mocker.patch.object(_sql_repository, "create_engine", return_value=sql_engine)
        repo = _VersionSQLRepository()

        version = _Version(id="1.0", config=Config._applied_config)
        repo._save(version)
        repo._set_latest_version(version.id)

        latest_1 = repo._get_latest_version()

        assert version.id == latest_1

        version.id = "2.0"
        repo._save(version)
        repo._set_latest_version(version.id)
        latest_2 = repo._get_latest_version()

        assert version.id != latest_1
        assert version.id == latest_2

    def test_get_set_development_version(self, mocker, sql_engine):
        Config.global_config.repository_type = "sql"
        mocker.patch.object(_sql_repository, "create_engine", return_value=sql_engine)
        repo = _VersionSQLRepository()

        version = _Version(id="1.0", config=Config._applied_config)
        repo._save(version)
        repo._set_development_version(version.id)

        dev_1 = repo._get_development_version()

        assert version.id == dev_1

        version.id = "2.0"
        repo._save(version)
        repo._set_development_version(version.id)
        dev_2 = repo._get_development_version()

        assert version.id != dev_1
        assert version.id == dev_2

    def test_get_set_production_version(self, mocker, sql_engine):
        Config.global_config.repository_type = "sql"
        mocker.patch.object(_sql_repository, "create_engine", return_value=sql_engine)
        repo = _VersionSQLRepository()

        version = _Version(id="1.0", config=Config._applied_config)
        repo._save(version)
        repo._set_production_version(version.id)

        prod_1 = repo._get_production_version()
        all_production_versions = [version.id]

        assert all_production_versions == prod_1

        version.id = "2.0"
        repo._save(version)
        repo._set_production_version(version.id)
        all_production_versions.append(version.id)
        prod_2 = repo._get_production_version()

        assert all_production_versions == prod_2

    def test_delete_production_version(self, mocker, sql_engine):
        Config.global_config.repository_type = "sql"
        mocker.patch.object(_sql_repository, "create_engine", return_value=sql_engine)
        repo = _VersionSQLRepository()

        version = _Version(id="1.0", config=Config._applied_config)
        repo._save(version)

        with pytest.raises(VersionIsNotProductionVersion):
            repo._delete_production_version(version.id)

        repo._set_production_version(version.id)
        assert len(repo._get_production_version()) == 1

        repo._delete_production_version(version.id)

        assert len(repo._get_production_version()) == 0
