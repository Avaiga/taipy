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

from .._version._version_manager import _VersionManager
from ..common._reload import _Reloader
from ..config import MigrationConfig


def _version_migration() -> str:
    """Add version attribute on old entities. Used to migrate from <=2.0 to >=2.1 version."""
    from ._version_cli import _VersioningCLI
    from ._version_manager import _VersionManager

    _VersioningCLI._create_parser()
    mode = _VersioningCLI._parse_arguments()[0]
    if mode != "development":
        return _VersionManager._get_latest_version()
    else:
        _VersionManager._get_or_create("LEGACY-VERSION", True)
        return "LEGACY-VERSION"


def _migrate_entity(entity):
    if (latest_version := _VersionManager._get_latest_version()) in _VersionManager._get_production_versions():
        with _Reloader():
            if migration_fcts := MigrationConfig._get_migration_fcts_to_latest(entity.version, entity.config_id):
                for fct in migration_fcts:
                    entity = fct(entity)
                entity.version = latest_version

    return entity
