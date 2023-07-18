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

import collections.abc
from copy import deepcopy
from typing import Any, Callable, Dict, Optional, Union

from taipy.config._config import _Config
from taipy.config.common._template_handler import _TemplateHandler as _tpl
from taipy.config.config import Config
from taipy.config.section import Section
from taipy.config.unique_section import UniqueSection


class MigrationConfig(UniqueSection):
    """
    Configuration fields needed to register migration functions from an old version to newer one.

    Attributes:
        migration_fcts (Dict[str, Dict[str, Callable]]): A dictionary that maps the version that entities are
            migrated from to the migration functions.
        **properties (dict[str, Any]): A dictionary of additional properties.
    """

    name = "VERSION_MIGRATION"

    _MIGRATION_FCTS_KEY = "migration_fcts"

    def __init__(
        self,
        migration_fcts: Dict[str, Dict[str, Callable]],
        **properties,
    ):
        self.migration_fcts = migration_fcts

        super().__init__(**properties)

    def __copy__(self):
        return MigrationConfig(
            deepcopy(self.migration_fcts),
            **deepcopy(self._properties),
        )

    def _clean(self):
        self.migration_fcts.clear()
        self._properties.clear()

    def __getattr__(self, item: str) -> Optional[Any]:
        return _tpl._replace_templates(self._properties.get(item))  # type: ignore

    @classmethod
    def default_config(cls):
        return MigrationConfig({})

    def _to_dict(self):
        return {
            self._MIGRATION_FCTS_KEY: self.migration_fcts,
            **self._properties,
        }

    @classmethod
    def _from_dict(cls, as_dict: Dict[str, Any], id: str, config: Optional[_Config]):
        return MigrationConfig(**as_dict)

    def _update(self, as_dict, default_section=None):
        def deep_update(d, u):
            for k, v in u.items():
                if isinstance(v, collections.abc.Mapping):
                    d[k] = deep_update(d.get(k, {}), v)
                else:
                    d[k] = v
            return d

        migration_fcts = as_dict.pop(self._MIGRATION_FCTS_KEY)
        deep_update(self.migration_fcts, migration_fcts)

        self._properties.update(as_dict)

    @staticmethod
    def _add_migration_function(
        target_version: str,
        config: Union[Section, str],
        migration_fct: Callable,
        **properties,
    ):
        """Add a migration function for a Configuration to migrate entities to the target version.

        Parameters:
            target_version (str): The production version that entities are migrated to.
            config (Union[Section, str]): The configuration or the `id` of the config that needs to migrate.
            migration_fct (Callable): Migration function that takes an entity as input and returns a new entity
                that is compatible with the target production version.
            **properties (Dict[str, Any]): A keyworded variable length list of additional arguments.
        Returns:
            `MigrationConfig^`: The Migration configuration.
        """
        config_id = config if isinstance(config, str) else config.id
        migration_fcts = {target_version: {config_id: migration_fct}}

        section = MigrationConfig(
            migration_fcts,
            **properties,
        )
        Config._register(section)
        return Config.unique_sections[MigrationConfig.name]
