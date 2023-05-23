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

from copy import copy
from typing import Any, Dict, Optional

from taipy.config import Config, UniqueSection
from taipy.config._config import _Config
from taipy.config.common._template_handler import _TemplateHandler as _tpl


class CoreSection(UniqueSection):
    name = "core"
    _MODE_KEY = "mode"
    _DEVELOPMENT_MODE = "development"
    _EXPERIMENT_MODE = "experiment"
    _PRODUCTION_MODE = "production"
    _DEFAULT_MODE = _DEVELOPMENT_MODE
    _VERSION_NUMBER_KEY = "version_number"
    _DEFAULT_VERSION_NUMBER = ""
    _TAIPY_FORCE_KEY = "force"
    _DEFAULT_TAIPY_FORCE = False
    _CLEAN_ENTITIES_KEY = "clean_entities"
    _DEFAULT_CLEAN_ENTITIES = False

    def __init__(
        self,
        mode: Optional[str] = None,
        version_number: Optional[str] = None,
        force: Optional[bool] = None,
        clean_entities: Optional[bool] = None,
        **properties,
    ):
        self.mode = mode or self._DEFAULT_MODE
        self.version_number = version_number or self._DEFAULT_VERSION_NUMBER
        self.force = force or self._DEFAULT_TAIPY_FORCE
        self.clean_entities = clean_entities or self._DEFAULT_CLEAN_ENTITIES
        super().__init__(**properties)

    def __copy__(self):
        return CoreSection(self.mode, self.version_number, self.force, self.clean_entities, **copy(self._properties))

    @classmethod
    def default_config(cls):
        return CoreSection(
            cls._DEFAULT_MODE, cls._DEFAULT_VERSION_NUMBER, cls._DEFAULT_TAIPY_FORCE, cls._DEFAULT_CLEAN_ENTITIES
        )

    def _to_dict(self):
        as_dict = {}
        if self.mode is not None:
            as_dict[self._MODE_KEY] = self.mode
        if self.version_number is not None:
            as_dict[self._VERSION_NUMBER_KEY] = self.version_number
        if self.force is not None:
            as_dict[self._TAIPY_FORCE_KEY] = self.force
        if self.clean_entities is not None:
            as_dict[self._CLEAN_ENTITIES_KEY] = self.clean_entities
        as_dict.update(self._properties)
        return as_dict

    @classmethod
    def _from_dict(cls, as_dict: Dict[str, Any], id=None, config: Optional[_Config] = None):
        mode = as_dict.pop(cls._MODE_KEY, None)
        version_nb = as_dict.pop(cls._VERSION_NUMBER_KEY, None)
        force = as_dict.pop(cls._TAIPY_FORCE_KEY, None)
        clean_entities = as_dict.pop(cls._CLEAN_ENTITIES_KEY, None)
        return CoreSection(mode, version_nb, force, clean_entities, **as_dict)

    def _update(self, as_dict: Dict[str, Any]):
        mode = _tpl._replace_templates(as_dict.pop(self._MODE_KEY, self.mode))
        if self.mode != mode:
            self.mode = mode
        version_number = _tpl._replace_templates(as_dict.pop(self._VERSION_NUMBER_KEY, self.version_number))
        if self.version_number != version_number:
            self.version_number = version_number
        force = _tpl._replace_templates(as_dict.pop(self._TAIPY_FORCE_KEY, self.force))
        if self.force != force:
            self.force = force
        clean_entities = _tpl._replace_templates(as_dict.pop(self._CLEAN_ENTITIES_KEY, self.clean_entities))
        if self.clean_entities != clean_entities:
            self.clean_entities = clean_entities
        self._properties.update(as_dict)

    @staticmethod
    def _configure(
        mode: Optional[str] = None,
        version_number: Optional[str] = None,
        force: Optional[bool] = None,
        clean_entities: Optional[bool] = None,
        **properties,
    ):
        """Configure the Core service.

        Parameters:
            **properties (Dict[str, Any]): A keyworded variable length list of additional arguments configure the
                behavior of the `Core^` service.
        Returns:
            The Core configuration.
        """
        section = CoreSection(
            mode=mode, version_number=version_number, force=force, clean_entities=clean_entities, **properties
        )
        Config._register(section)
        return Config.unique_sections[CoreSection.name]
