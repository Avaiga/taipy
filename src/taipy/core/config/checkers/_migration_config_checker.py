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

from taipy.config._config import _Config
from taipy.config.checker._checkers._config_checker import _ConfigChecker
from taipy.config.checker.issue_collector import IssueCollector

from ..._version._version_manager_factory import _VersionManagerFactory
from ..migration_config import MigrationConfig


class _MigrationConfigChecker(_ConfigChecker):
    def __init__(self, config: _Config, collector: IssueCollector):
        super().__init__(config, collector)

    def _check(self) -> IssueCollector:
        if migration_config := self._config._unique_sections.get(MigrationConfig.name):
            self._check_if_entity_property_key_used_is_predefined(migration_config)

            migration_fcts = migration_config.migration_fcts

            for target_version, migration_functions in migration_config.migration_fcts.items():
                for config_id, migration_function in migration_functions.items():
                    self._check_callable(target_version, config_id, migration_function)

            self._check_valid_production_version(migration_fcts)
            self._check_migration_from_productions_to_productions_exist(migration_fcts)

        return self._collector

    def _check_callable(self, target_version, config_id, migration_function):
        if not callable(migration_function):
            self._error(
                MigrationConfig._MIGRATION_FCTS_KEY,
                migration_function,
                f"The migration function of config `{config_id}` from version {target_version}"
                f" must be populated with Callable value.",
            )

    def _check_valid_production_version(self, migration_fcts):
        for target_version in migration_fcts.keys():
            if target_version not in _VersionManagerFactory._build_manager()._get_production_versions():
                self._error(
                    MigrationConfig._MIGRATION_FCTS_KEY,
                    target_version,
                    "The target version for a migration function must be a production version.",
                )

    def _check_migration_from_productions_to_productions_exist(self, migration_fcts):
        production_versions = _VersionManagerFactory._build_manager()._get_production_versions()
        for source_version, target_version in zip(production_versions[:-1], production_versions[1:]):
            if not migration_fcts.get(target_version):
                self._info(
                    "target_version",
                    None,
                    f'There is no migration function from production version "{source_version}"'
                    f' to version "{target_version}".',
                )
