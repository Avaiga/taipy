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

import re
from copy import copy
from typing import Any, Dict, Optional, Union

from taipy.common.config import Config, UniqueSection
from taipy.common.config._config import _Config
from taipy.common.config.common._config_blocker import _ConfigBlocker
from taipy.common.config.common._template_handler import _TemplateHandler as _tpl
from taipy.core._version._version_manager_factory import _VersionManagerFactory
from taipy.core.cycle._cycle_manager_factory import _CycleManagerFactory
from taipy.core.data._data_manager_factory import _DataManagerFactory
from taipy.core.job._job_manager_factory import _JobManagerFactory
from taipy.core.scenario._scenario_manager_factory import _ScenarioManagerFactory
from taipy.core.sequence._sequence_manager_factory import _SequenceManagerFactory
from taipy.core.submission._submission_manager_factory import _SubmissionManagerFactory
from taipy.core.task._task_manager_factory import _TaskManagerFactory

from .._init_version import _read_version
from ..exceptions.exceptions import ConfigCoreVersionMismatched


class CoreSection(UniqueSection):
    """Configuration parameters for running the `Orchestrator^` service."""

    name: str = "CORE"

    _ROOT_FOLDER_KEY = "root_folder"
    _DEFAULT_ROOT_FOLDER = "./taipy/"

    _STORAGE_FOLDER_KEY = "storage_folder"
    _DEFAULT_STORAGE_FOLDER = "user_data/"

    _STORAGE_FOLDER_TP_KEY = "taipy_storage_folder"
    _DEFAULT_STORAGE_FOLDER_TP = ".taipy/"

    _REPOSITORY_TYPE_KEY = "repository_type"
    _DEFAULT_REPOSITORY_TYPE = "filesystem"
    _REPOSITORY_PROPERTIES_KEY = "repository_properties"
    _DEFAULT_REPOSITORY_PROPERTIES: Dict = {}

    _READ_ENTITY_RETRY_KEY = "read_entity_retry"
    _DEFAULT_READ_ENTITY_RETRY = 1

    _MODE_KEY = "mode"
    _DEFAULT_MODE = "development"

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
        taipy_storage_folder: Optional[str] = None,
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
        self._taipy_storage_folder = taipy_storage_folder
        self._repository_type = repository_type
        self._repository_properties = repository_properties
        self._read_entity_retry = read_entity_retry
        self._mode = mode
        self._version_number = version_number
        self._force = force

        self._check_compatibility(core_version)
        self._core_version = core_version

        super().__init__(**properties)

    def __copy__(self) -> "CoreSection":
        return CoreSection(
            self.root_folder,
            self.storage_folder,
            self.taipy_storage_folder,
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
    def root_folder(self) -> str:
        """ Path of the base folder for the taipy application.

        The default value is "./taipy/".
        """
        return _tpl._replace_templates(self._root_folder)

    @root_folder.setter  # type: ignore
    @_ConfigBlocker._check()
    def root_folder(self, val) -> None:
        self._root_folder = val

    @property
    def storage_folder(self) -> str:
        """Folder name used to store user data.

        The default value is "user_data/".

        It is used in conjunction with the *root_folder* attribute. That means the storage path is
        <root_folder><storage_folder> (The default path is "./taipy/user_data/").
        """
        return _tpl._replace_templates(self._storage_folder)

    @storage_folder.setter  # type: ignore
    @_ConfigBlocker._check()
    def storage_folder(self, val) -> None:
        self._storage_folder = val

    @property
    def taipy_storage_folder(self) -> str:
        """Folder name used to store internal Taipy data.

        The default value is ".taipy/".
        """
        return _tpl._replace_templates(self._taipy_storage_folder)

    @taipy_storage_folder.setter  # type: ignore
    @_ConfigBlocker._check()
    def taipy_storage_folder(self, val) -> None:
        self._taipy_storage_folder = val

    @property
    def repository_type(self) -> str:
        """Type of the repository to be used to store Taipy data.

        The default value is "filesystem".
        """
        return _tpl._replace_templates(self._repository_type)

    @repository_type.setter  # type: ignore
    @_ConfigBlocker._check()
    def repository_type(self, val) -> None:
        self._repository_type = val
        CoreSection.__reload_repositories()

    @property
    def repository_properties(self) -> Dict[str, Union[str, int]]:
        """A dictionary of additional properties to be used by the repository."""
        return (
            {k: _tpl._replace_templates(v) for k, v in self._repository_properties.items()}
            if self._repository_properties
            else self._DEFAULT_REPOSITORY_PROPERTIES.copy()
        )

    @repository_properties.setter  # type: ignore
    @_ConfigBlocker._check()
    def repository_properties(self, val) -> None:
        self._repository_properties = val

    @property
    def read_entity_retry(self) -> int:
        """Number of retries to read an entity from the repository before return failure.

        The default value is 3.
        """
        return _tpl._replace_templates(self._read_entity_retry)

    @read_entity_retry.setter  # type: ignore
    @_ConfigBlocker._check()
    def read_entity_retry(self, val) -> None:
        self._read_entity_retry = val

    @property
    def mode(self) -> str:
        """The operating mode of Taipy.

        Taipy applications are versioned. The versioning system is used to manage
        the different versions of the user application. Depending on the
        operating mode, Taipy will behave differently when a version of the
        application runs. Three modes are available: "development", "experiment",
        and "production". Please refer to the
        [Versioning management](../../../../../../userman/advanced_features/versioning/index.md)
        documentation page for more details.

        By default, Taipy runs in "development" mode.
        """
        return _tpl._replace_templates(self._mode)

    @mode.setter  # type: ignore
    @_ConfigBlocker._check()
    def mode(self, val) -> None:
        self._mode = val

    @property
    def version_number(self) -> str:
        """The identifier of the user application version.

        Please refer to the
        [Versioning management](../../../../../../userman/advanced_features/versioning/index.md)
        documentation page for more details.
        """
        return _tpl._replace_templates(self._version_number)

    @version_number.setter  # type: ignore
    @_ConfigBlocker._check()
    def version_number(self, val) -> None:
        self._version_number = val

    @property
    def force(self) -> bool:
        """If True, force the run of a user application.

        If the configuration of the application current version has some conflicts with
        the configuration of the last run application, Taipy will exit. If the *force*
        attribute is set to True, Taipy will run even if there are some conflicts.
        """
        return _tpl._replace_templates(self._force)

    @force.setter  # type: ignore
    @_ConfigBlocker._check()
    def force(self, val) -> None:
        self._force = val

    @property
    def core_version(self) -> str:
        """The version of the Taipy core library."""
        return _tpl._replace_templates(self._core_version)

    @classmethod
    def default_config(cls) -> "CoreSection":
        """Return a core section with all the default values.

        Returns:
            The default core section.
        """
        return CoreSection(
            cls._DEFAULT_ROOT_FOLDER,
            cls._DEFAULT_STORAGE_FOLDER,
            cls._DEFAULT_STORAGE_FOLDER_TP,
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
        self._taipy_storage_folder = self._DEFAULT_STORAGE_FOLDER
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
        if self._taipy_storage_folder:
            as_dict[self._STORAGE_FOLDER_TP_KEY] = self._taipy_storage_folder
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
        taipy_storage_folder = as_dict.pop(cls._STORAGE_FOLDER_TP_KEY, None)
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
            taipy_storage_folder,
            repository_type,
            repository_properties,
            read_entity_retry,
            mode,
            version_nb,
            force,
            core_version,
            **as_dict,
        )

    def _update(self, as_dict: Dict[str, Any], default_section=None):
        self._root_folder = as_dict.pop(self._ROOT_FOLDER_KEY, self._root_folder)
        self._storage_folder = as_dict.pop(self._STORAGE_FOLDER_KEY, self._storage_folder)
        self._taipy_storage_folder = as_dict.pop(self._STORAGE_FOLDER_TP_KEY, self._taipy_storage_folder)
        self._repository_type = as_dict.pop(self._REPOSITORY_TYPE_KEY, self._repository_type)
        if self._repository_properties is None:
            self._repository_properties = as_dict.pop(
                self._REPOSITORY_PROPERTIES_KEY, self._DEFAULT_REPOSITORY_PROPERTIES.copy()
            )
        else:
            self._repository_properties.update(
                as_dict.pop(self._REPOSITORY_PROPERTIES_KEY, self._repository_properties)
            )
        self._read_entity_retry = as_dict.pop(self._READ_ENTITY_RETRY_KEY, self._read_entity_retry)
        self._mode = as_dict.pop(self._MODE_KEY, self.mode)
        self._version_number = as_dict.pop(self._VERSION_NUMBER_KEY, self.version_number)
        self._force = as_dict.pop(self._FORCE_KEY, self.force)

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
        taipy_storage_folder: Optional[str] = None,
        repository_type: Optional[str] = None,
        repository_properties: Optional[Dict[str, Union[str, int]]] = None,
        read_entity_retry: Optional[int] = None,
        mode: Optional[str] = None,
        version_number: Optional[str] = None,
        force: Optional[bool] = None,
        **properties,
    ) -> "CoreSection":
        """Configure the Orchestrator service.

        Parameters:
            root_folder (Optional[str]): Path of the base folder for the taipy application.
                The default value is "./taipy/"
            storage_folder (str): Folder name used to store user data. The default value is "user_data/". It is used in
                conjunction with the *root_folder* attribute. That means the storage path is
                <root_folder><storage_folder> (The default path is "./taipy/user_data/").
            taipy_storage_folder (str): Folder name used to store Taipy data. The default value is ".taipy/". It is
                used in conjunction with the *root_folder* attribute. That means the storage path is
                <root_folder><storage_folder> (The default path is "./taipy/.taipy/").
            repository_type (Optional[str]): The type of the repository to be used to store Taipy data.
                The default value is "filesystem".
            repository_properties (Optional[Dict[str, Union[str, int]]]): A dictionary of additional properties
                to be used by the repository.
            read_entity_retry (Optional[int]): Number of retries to read an entity from the repository
                before return failure. The default value is 3.
            mode (Optional[str]): Indicates the mode of the version management system.
                Possible values are *"development"* or *"experiment"*. On Enterprise edition of Taipy,
                *production* mode is also available. Please refer to the
                [Versioning management](../../../../../../userman/advanced_features/versioning/index.md)
                documentation page for more details.
            version_number (Optional[str]): The string identifier of the version.
                 In development mode, the version number is ignored.
            force (Optional[bool]): If True, Taipy will override a version even if the configuration
                has changed and run the application.
            **properties (Dict[str, Any]): A keyworded variable length list of additional arguments configure the
                behavior of the `Orchestrator^` service.

        Returns:
            The Core configuration.
        """
        section = CoreSection(
            root_folder=root_folder,
            storage_folder=storage_folder,
            taipy_storage_folder=taipy_storage_folder,
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

        if repository_type:
            CoreSection.__reload_repositories()

        return Config.unique_sections[CoreSection.name]

    @staticmethod
    def __reload_repositories():
        _CycleManagerFactory._build_manager.cache_clear()
        _SequenceManagerFactory._build_manager.cache_clear()
        _ScenarioManagerFactory._build_manager.cache_clear()
        _TaskManagerFactory._build_manager.cache_clear()
        _JobManagerFactory._build_manager.cache_clear()
        _DataManagerFactory._build_manager.cache_clear()
        _SubmissionManagerFactory._build_manager.cache_clear()
        _VersionManagerFactory._build_manager.cache_clear()
