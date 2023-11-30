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

from typing import Callable, List

from taipy.config.config import Config

from .._entity._reload import _Reloader
from ..config import MigrationConfig
from ._version_manager_factory import _VersionManagerFactory


def _migrate_entity(entity):
    if (
        latest_version := _VersionManagerFactory._build_manager()._get_latest_version()
    ) in _VersionManagerFactory._build_manager()._get_production_versions():
        if migration_fcts := __get_migration_fcts_to_latest(entity._version, entity.config_id):
            with _Reloader():
                for fct in migration_fcts:
                    entity = fct(entity)
                entity._version = latest_version

    return entity


def __get_migration_fcts_to_latest(source_version: str, config_id: str) -> List[Callable]:
    migration_fcts_to_latest: List[Callable] = []

    production_versions = _VersionManagerFactory._build_manager()._get_production_versions()
    try:
        start_index = production_versions.index(source_version) + 1
    except ValueError:
        return migration_fcts_to_latest

    versions_to_migrate = production_versions[start_index:]

    for version in versions_to_migrate:
        migration_fct = Config.unique_sections[MigrationConfig.name].migration_fcts.get(version, {}).get(config_id)
        if migration_fct:
            migration_fcts_to_latest.append(migration_fct)

    return migration_fcts_to_latest
