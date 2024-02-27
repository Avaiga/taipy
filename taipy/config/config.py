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

import os
from typing import Dict

from ..logger._taipy_logger import _TaipyLogger
from ._config import _Config
from ._config_comparator._config_comparator import _ConfigComparator
from ._serializer._json_serializer import _JsonSerializer
from ._serializer._toml_serializer import _TomlSerializer
from .checker._checker import _Checker
from .checker.issue_collector import IssueCollector
from .common._classproperty import _Classproperty
from .common._config_blocker import _ConfigBlocker
from .global_app.global_app_config import GlobalAppConfig
from .section import Section
from .unique_section import UniqueSection


class Config:
    """Configuration singleton."""

    _ENVIRONMENT_VARIABLE_NAME_WITH_CONFIG_PATH = "TAIPY_CONFIG_PATH"
    __logger = _TaipyLogger._get_logger()
    _default_config = _Config._default_config()
    _python_config = _Config()
    _file_config = _Config()
    _env_file_config = _Config()
    _applied_config = _Config()
    _collector = IssueCollector()
    _serializer = _TomlSerializer()
    __json_serializer = _JsonSerializer()
    _comparator: _ConfigComparator = _ConfigComparator()

    @_Classproperty
    def unique_sections(cls) -> Dict[str, UniqueSection]:
        """Return all unique sections."""
        return cls._applied_config._unique_sections

    @_Classproperty
    def sections(cls) -> Dict[str, Dict[str, Section]]:
        """Return all non unique sections."""
        return cls._applied_config._sections

    @_Classproperty
    def global_config(cls) -> GlobalAppConfig:
        """Return configuration values related to the global application as a `GlobalAppConfig^`."""
        return cls._applied_config._global_config

    @classmethod
    @_ConfigBlocker._check()
    def load(cls, filename):
        """Load a configuration file.

        The current Python configuration is replaced and the Config compilation is triggered.

        Parameters:
            filename (Union[str, Path]): The path of the toml configuration file to load.
        """
        cls.__logger.info(f"Loading configuration. Filename: '{filename}'")
        cls._python_config = cls._serializer._read(filename)
        cls._compile_configs()
        cls.__logger.info(f"Configuration '{filename}' successfully loaded.")

    @classmethod
    def export(cls, filename):
        """Export a configuration.

        The export is done in a toml file.

        The exported configuration is taken from the Python code configuration.

        Parameters:
            filename (Union[str, Path]): The path of the file to export.
        Note:
            If *filename* already exists, it is overwritten.
        """
        cls._serializer._write(cls._python_config, filename)

    @classmethod
    def backup(cls, filename):
        """Backup a configuration.

        The backup is done in a toml file.

        The backed up configuration is a compilation from the three possible methods to configure
        the application: the Python code configuration, the file configuration and the environment
        configuration.

        Parameters:
            filename (Union[str, Path]): The path of the file to export.
        Note:
            If *filename* already exists, it is overwritten.
        """
        cls._serializer._write(cls._applied_config, filename)

    @classmethod
    @_ConfigBlocker._check()
    def restore(cls, filename):
        """Restore a configuration file and replace the current applied configuration.

        Parameters:
            filename (Union[str, Path]): The path of the toml configuration file to load.
        """
        cls.__logger.info(f"Restoring configuration. Filename: '{filename}'")
        cls._applied_config = cls._serializer._read(filename)
        cls.__logger.info(f"Configuration '{filename}' successfully restored.")

    @classmethod
    @_ConfigBlocker._check()
    def override(cls, filename):
        """Load a configuration from a file and overrides the current config.

        Parameters:
            filename (Union[str, Path]): The path of the toml configuration file to load.
        """
        cls.__logger.info(f"Loading configuration. Filename: '{filename}'")
        cls._file_config = cls._serializer._read(filename)
        cls.__logger.info("Overriding configuration.'")
        cls._compile_configs()
        cls.__logger.info(f"Configuration '{filename}' successfully loaded.")

    @classmethod
    def block_update(cls):
        """Block update on the configuration signgleton."""
        _ConfigBlocker._block()

    @classmethod
    def unblock_update(cls):
        """Unblock update on the configuration signgleton."""
        _ConfigBlocker._unblock()

    @classmethod
    @_ConfigBlocker._check()
    def configure_global_app(cls, **properties) -> GlobalAppConfig:
        """Configure the global application.

        Parameters:
            **properties (Dict[str, Any]): A dictionary of additional properties.
        Returns:
            The global application configuration.
        """
        glob_cfg = GlobalAppConfig(**properties)
        if cls._python_config._global_config is None:
            cls._python_config._global_config = glob_cfg
        else:
            cls._python_config._global_config._update(glob_cfg._to_dict())
        cls._compile_configs()
        return cls._applied_config._global_config

    @classmethod
    def check(cls) -> IssueCollector:
        """Check configuration.

        This method logs issue messages and returns an issue collector.

        Returns:
            Collector containing the info, warning and error issues.
        """
        cls._collector = _Checker._check(cls._applied_config)
        cls.__log_message(cls)
        return cls._collector

    @classmethod
    @_ConfigBlocker._check()
    def _register_default(cls, default_section: Section):
        if isinstance(default_section, UniqueSection):
            if cls._default_config._unique_sections.get(default_section.name, None):
                cls._default_config._unique_sections[default_section.name]._update(default_section._to_dict())
            else:
                cls._default_config._unique_sections[default_section.name] = default_section
        elif def_sections := cls._default_config._sections.get(default_section.name, None):
                def_sections[default_section.id] = default_section
        else:
            cls._default_config._sections[default_section.name] = {default_section.id: default_section}
        cls._serializer._section_class[default_section.name] = default_section.__class__  # type: ignore
        cls.__json_serializer._section_class[default_section.name] = default_section.__class__  # type: ignore
        cls._compile_configs()

    @classmethod
    @_ConfigBlocker._check()
    def _register(cls, section):
        if isinstance(section, UniqueSection):
            if cls._python_config._unique_sections.get(section.name, None):
                cls._python_config._unique_sections[section.name]._update(section._to_dict())
            else:
                cls._python_config._unique_sections[section.name] = section
        elif sections := cls._python_config._sections.get(section.name, None):
            if sections.get(section.id, None):
                sections[section.id]._update(section._to_dict())
            else:
                sections[section.id] = section
        else:
            cls._python_config._sections[section.name] = {section.id: section}
        cls._serializer._section_class[section.name] = section.__class__
        cls.__json_serializer._section_class[section.name] = section.__class__
        cls._compile_configs()

    @classmethod
    def _override_env_file(cls):
        if config_filename := os.environ.get(cls._ENVIRONMENT_VARIABLE_NAME_WITH_CONFIG_PATH):
            cls.__logger.info(f"Loading configuration provided by environment variable. Filename: '{config_filename}'")
            cls._env_file_config = cls._serializer._read(config_filename)
            cls.__logger.info(f"Configuration '{config_filename}' successfully loaded.")

    @classmethod
    def _compile_configs(cls):
        Config._override_env_file()
        cls._applied_config._clean()
        if cls._default_config:
            cls._applied_config._update(cls._default_config)
        if cls._python_config:
            cls._applied_config._update(cls._python_config)
        if cls._file_config:
            cls._applied_config._update(cls._file_config)
        if cls._env_file_config:
            cls._applied_config._update(cls._env_file_config)

    @classmethod
    def __log_message(cls, config):
        for issue in config._collector._warnings:
            cls.__logger.warning(str(issue))
        for issue in config._collector._infos:
            cls.__logger.info(str(issue))
        for issue in config._collector._errors:
            cls.__logger.error(str(issue))
        if len(config._collector._errors) != 0:
            raise SystemExit("Configuration errors found. Please check the error log for more information.")

    @classmethod
    def _to_json(cls, _config: _Config) -> str:
        return cls.__json_serializer._serialize(_config)

    @classmethod
    def _from_json(cls, config_as_str: str) -> _Config:
        return cls.__json_serializer._deserialize(config_as_str)


Config._override_env_file()
