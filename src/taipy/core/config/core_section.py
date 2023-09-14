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

import re
from copy import copy
from typing import Any, Dict, Optional, Union

from taipy.config import Config, UniqueSection
from taipy.config._config import _Config
from taipy.config.common._config_blocker import _ConfigBlocker
from taipy.config.common._template_handler import _TemplateHandler as _tpl

from .._init_version import _read_version
from ..exceptions.exceptions import ConfigCoreVersionMismatched


class CoreSection(UniqueSection):
    """
    Configuration parameters for running the `Core^` service.


    Attributes:
        root_folder (str): Path of the base folder for the taipy application. The default value is "./taipy/"
        storage_folder (str): Folder name used to store Taipy data. The default value is ".data/". It is used in
            conjunction with the `root_folder` field. That means the storage path is <root_folder><storage_folder>
            (The default path is "./taipy/.data/").
        repository_type (str): Type of the repository to be used to store Taipy data. The default value is "filesystem".
        repository_properties (Dict[str, Union[str, int]]): A dictionary of additional properties to be used by the
            repository.
        read_entity_retry (int): Number of retries to read an entity from the repository before return failure.
            The default value is 3.
        mode (str): The Taipy operating mode. By default, the `Core^` service runs in "development" mode.
            An "experiment" and a "production" mode are also available. Please refer to the
            [Versioning management](../../core/versioning/) documentation page for more details.
        version_number (str)): The identifier of the user application version. Please refer to the
            [Versioning management](../../core/versioning/) documentation page for more details.
        force (bool): If True, force the application run even if there are some conflicts in the
            configuration.
        **properties (dict[str, any]): A dictionary of additional properties.
    """

    name = "CORE"

    _ROOT_FOLDER_KEY = "root_folder"
    _DEFAULT_ROOT_FOLDER = "./taipy/"

    _STORAGE_FOLDER_KEY = "storage_folder"
    _DEFAULT_STORAGE_FOLDER = ".data/"

    _REPOSITORY_TYPE_KEY = "repository_type"
    _DEFAULT_REPOSITORY_TYPE = "filesystem"
    _REPOSITORY_PROPERTIES_KEY = "repository_properties"
    _DEFAULT_REPOSITORY_PROPERTIES: Dict = dict()

    _READ_ENTITY_RETRY_KEY = "read_entity_retry"
    _DEFAULT_READ_ENTITY_RETRY = 1

    _MODE_KEY = "mode"
    _DEVELOPMENT_MODE = "development"
    _EXPERIMENT_MODE = "experiment"
    _PRODUCTION_MODE = "production"
    _DEFAULT_MODE = _DEVELOPMENT_MODE

    _VERSION_NUMBER_KEY = "version_number"
    _DEFAULT_VERSION_NUMBER = ""

    _FORCE_KEY = "force"
    _DEFAULT_FORCE = False

    _CORE_VERSION_KEY = "core_version"
    _CURRENT_CORE_VERSION = _read_version()

    def __init__(
        self,
        root_folder: Optional[str] = None,
        storage_folder: Optional[str] = None,
        repository_type: Optional[str] = None,
        repository_properties: Optional[Dict[str, Union[str, int]]] = None,
        read_entity_retry: Optional[int] = None,
        mode: Optional[str] = None,
        version_number: Optional[str] = None,
        force: Optional[bool] = None,
        core_version: Optional[str] = None,
        **properties,
    ):
        self._root_folder = root_folder
        self._storage_folder = storage_folder
        self._repository_type = repository_type
        self._repository_properties = repository_properties or {}
        self._read_entity_retry = (
            read_entity_retry if read_entity_retry is not None else self._DEFAULT_READ_ENTITY_RETRY
        )
        self.mode = mode or self._DEFAULT_MODE
        self.version_number = version_number or self._DEFAULT_VERSION_NUMBER
        self.force = force or self._DEFAULT_FORCE

        self._check_compatibility(core_version)
        self._core_version = core_version

        super().__init__(**properties)

    def __copy__(self):
        return CoreSection(
            self.root_folder,
            self.storage_folder,
            self.repository_type,
            self.repository_properties,
            self.read_entity_retry,
            self.mode,
            self.version_number,
            self.force,
            self._core_version,
            **copy(self._properties),
        )

    @property
    def storage_folder(self):
        return _tpl._replace_templates(self._storage_folder)

    @storage_folder.setter  # type: ignore
    @_ConfigBlocker._check()
    def storage_folder(self, val):
        self._storage_folder = val

    @property
    def root_folder(self):
        return _tpl._replace_templates(self._root_folder)

    @root_folder.setter  # type: ignore
    @_ConfigBlocker._check()
    def root_folder(self, val):
        self._root_folder = val

    @property
    def repository_type(self):
        return _tpl._replace_templates(self._repository_type)

    @repository_type.setter  # type: ignore
    @_ConfigBlocker._check()
    def repository_type(self, val):
        self._repository_type = val

    @property
    def repository_properties(self):
        return (
            {k: _tpl._replace_templates(v) for k, v in self._repository_properties.items()}
            if self._repository_properties
            else self._DEFAULT_REPOSITORY_PROPERTIES.copy()
        )

    @repository_properties.setter  # type: ignore
    @_ConfigBlocker._check()
    def repository_properties(self, val):
        self._repository_properties = val

    @property
    def read_entity_retry(self):
        return _tpl._replace_templates(self._read_entity_retry)

    @read_entity_retry.setter  # type: ignore
    @_ConfigBlocker._check()
    def read_entity_retry(self, val):
        self._read_entity_retry = val

    @classmethod
    def default_config(cls):
        return CoreSection(
            cls._DEFAULT_ROOT_FOLDER,
            cls._DEFAULT_STORAGE_FOLDER,
            cls._DEFAULT_REPOSITORY_TYPE,
            cls._DEFAULT_REPOSITORY_PROPERTIES,
            cls._DEFAULT_READ_ENTITY_RETRY,
            cls._DEFAULT_MODE,
            cls._DEFAULT_VERSION_NUMBER,
            cls._DEFAULT_FORCE,
            cls._CURRENT_CORE_VERSION,
        )

    def _clean(self):
        self._root_folder = self._DEFAULT_ROOT_FOLDER
        self._storage_folder = self._DEFAULT_STORAGE_FOLDER
        self._repository_type = self._DEFAULT_REPOSITORY_TYPE
        self._repository_properties = self._DEFAULT_REPOSITORY_PROPERTIES.copy()
        self._read_entity_retry = self._DEFAULT_READ_ENTITY_RETRY
        self.mode = self._DEFAULT_MODE
        self.version_number = self._DEFAULT_VERSION_NUMBER
        self.force = self._DEFAULT_FORCE
        self._core_version = self._CURRENT_CORE_VERSION
        self._properties.clear()

    def _to_dict(self):
        as_dict = {}
        if self._root_folder:
            as_dict[self._ROOT_FOLDER_KEY] = self._root_folder
        if self._storage_folder:
            as_dict[self._STORAGE_FOLDER_KEY] = self._storage_folder
        if self._repository_type:
            as_dict[self._REPOSITORY_TYPE_KEY] = self._repository_type
        if self._repository_properties:
            as_dict[self._REPOSITORY_PROPERTIES_KEY] = self._repository_properties
        if self._read_entity_retry is not None:
            as_dict[self._READ_ENTITY_RETRY_KEY] = self._read_entity_retry
        if self.mode is not None:
            as_dict[self._MODE_KEY] = self.mode
        if self.version_number is not None:
            as_dict[self._VERSION_NUMBER_KEY] = self.version_number
        if self.force is not None:
            as_dict[self._FORCE_KEY] = self.force
        if self._core_version is not None:
            as_dict[self._CORE_VERSION_KEY] = self._core_version
        as_dict.update(self._properties)
        return as_dict

    @classmethod
    def _from_dict(cls, as_dict: Dict[str, Any], id=None, config: Optional[_Config] = None):
        root_folder = as_dict.pop(cls._ROOT_FOLDER_KEY, None)
        storage_folder = as_dict.pop(cls._STORAGE_FOLDER_KEY, None)
        repository_type = as_dict.pop(cls._REPOSITORY_TYPE_KEY, None)
        repository_properties = as_dict.pop(cls._REPOSITORY_PROPERTIES_KEY, None)
        read_entity_retry = as_dict.pop(cls._READ_ENTITY_RETRY_KEY, None)
        mode = as_dict.pop(cls._MODE_KEY, None)
        version_nb = as_dict.pop(cls._VERSION_NUMBER_KEY, None)
        force = as_dict.pop(cls._FORCE_KEY, None)
        core_version = as_dict.pop(cls._CORE_VERSION_KEY, None)
        return CoreSection(
            root_folder,
            storage_folder,
            repository_type,
            repository_properties,
            read_entity_retry,
            mode,
            version_nb,
            force,
            core_version,
            **as_dict,
        )

    def _update(self, as_dict: Dict[str, Any]):
        root_folder = _tpl._replace_templates(as_dict.pop(self._ROOT_FOLDER_KEY, self._root_folder))
        if self._root_folder != root_folder:
            self._root_folder = root_folder

        storage_folder = _tpl._replace_templates(as_dict.pop(self._STORAGE_FOLDER_KEY, self._storage_folder))
        if self._storage_folder != storage_folder:
            self._storage_folder = storage_folder

        repository_type = _tpl._replace_templates(as_dict.pop(self._REPOSITORY_TYPE_KEY, self._repository_type))
        if self._repository_type != repository_type:
            self._repository_type = repository_type

        repository_properties = _tpl._replace_templates(
            as_dict.pop(self._REPOSITORY_PROPERTIES_KEY, self._repository_properties)
        )
        self._repository_properties.update(repository_properties)

        read_entity_retry = _tpl._replace_templates(as_dict.pop(self._READ_ENTITY_RETRY_KEY, self._read_entity_retry))
        if self._read_entity_retry != read_entity_retry:
            self._read_entity_retry = read_entity_retry

        mode = _tpl._replace_templates(as_dict.pop(self._MODE_KEY, self.mode))
        if self.mode != mode:
            self.mode = mode

        version_number = _tpl._replace_templates(as_dict.pop(self._VERSION_NUMBER_KEY, self.version_number))
        if self.version_number != version_number:
            self.version_number = version_number

        force = _tpl._replace_templates(as_dict.pop(self._FORCE_KEY, self.force))
        if self.force != force:
            self.force = force

        core_version = as_dict.pop(self._CORE_VERSION_KEY, None)
        self._check_compatibility(core_version)

        self._properties.update(as_dict)

    @classmethod
    def _check_compatibility(cls, core_version):
        if not core_version:
            return

        version_pattern = r"^(\d+)\.(\d+)\.(\d+)$"
        dev_version_pattern = r"^(\d+)\.(\d+)\.(\d+).(\w*)$"

        installed_match = re.match(version_pattern, cls._CURRENT_CORE_VERSION) or re.match(
            dev_version_pattern, cls._CURRENT_CORE_VERSION
        )
        required_match = re.match(version_pattern, core_version) or re.match(dev_version_pattern, core_version)
        if required_match and installed_match:
            installed_group = installed_match.groups()
            required_group = required_match.groups()
            installed_major, installed_minor = installed_group[0], installed_group[1]
            required_major, required_minor = required_group[0], required_group[1]

            if required_major != installed_major or required_minor != installed_minor:
                raise ConfigCoreVersionMismatched(core_version, cls._CURRENT_CORE_VERSION)

    @staticmethod
    def _configure(
        root_folder: Optional[str] = None,
        storage_folder: Optional[str] = None,
        repository_type: Optional[str] = None,
        repository_properties: Optional[Dict[str, Union[str, int]]] = None,
        read_entity_retry: Optional[int] = None,
        mode: Optional[str] = None,
        version_number: Optional[str] = None,
        force: Optional[bool] = None,
        **properties,
    ) -> "CoreSection":
        """Configure the Core service.

        Parameters:
            root_folder (Optional[str]): Path of the base folder for the taipy application.
                The default value is "./taipy/"
            storage_folder (Optional[str]): Folder name used to store Taipy data. The default value is ".data/".
                It is used in conjunction with the `root_folder` field. That means the storage path is
                <root_folder><storage_folder> (The default path is "./taipy/.data/").
            repository_type (Optional[str]): The type of the repository to be used to store Taipy data.
                The default value is "filesystem".
            repository_properties (Optional[Dict[str, Union[str, int]]]): A dictionary of additional properties
                to be used by the repository.
            read_entity_retry (Optional[int]): Number of retries to read an entity from the repository
                before return failure. The default value is 3.
            mode (Optional[str]): Indicates the mode of the version management system.
                Possible values are *"development"*, *"experiment"*, or *"production"*.
            version_number (Optional[str]): The string identifier of the version.
                 In development mode, the version number is ignored.
            force (Optional[bool]): If True, Taipy will override a version even if the configuration
                has changed and run the application.
            **properties (Dict[str, Any]): A keyworded variable length list of additional arguments configure the
                behavior of the `Core^` service.
        Returns:
            The Core configuration.
        """
        section = CoreSection(
            root_folder=root_folder,
            storage_folder=storage_folder,
            repository_type=repository_type,
            repository_properties=repository_properties,
            read_entity_retry=read_entity_retry,
            mode=mode,
            version_number=version_number,
            force=force,
            core_version=_read_version(),
            **properties,
        )
        Config._register(section)
        return Config.unique_sections[CoreSection.name]
