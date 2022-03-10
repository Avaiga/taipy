from __future__ import annotations

from typing import Any, Dict, Optional, Union

from taipy.core.config._config_template_handler import _ConfigTemplateHandler as _tpl


class GlobalAppConfig:
    """
    Configuration fields related to the global application.

    Parameters:
        root_folder (str): Path of the base folder for the taipy application. The default value is "./taipy/"
        storage_folder (str): Folder name used to store Taipy data. The default value is ".data/". It is used in
            conjunction with the `root_folder` field. That means the storage path is <root_folder><storage_folder>
            (The Default path is "./taipy/.data/").
        clean_entities_enabled (bool): Boolean field to activate/deactivate the clean entities feature. Default: false
        **properties (dict[str, Any]): A dictionary of additional properties.
    """

    _ROOT_FOLDER_KEY = "root_folder"
    _DEFAULT_ROOT_FOLDER = "./taipy/"

    _STORAGE_FOLDER_KEY = "storage_folder"
    _DEFAULT_STORAGE_FOLDER = ".data/"

    _CLEAN_ENTITIES_ENABLED_KEY = "clean_entities_enabled"
    _DEFAULT_CLEAN_ENTITIES_ENABLED = False
    _CLEAN_ENTITIES_ENABLED_ENV_VAR = "TAIPY_CLEAN_ENTITIES_ENABLED"
    _CLEAN_ENTITIES_ENABLED_TEMPLATE = f"ENV[{_CLEAN_ENTITIES_ENABLED_ENV_VAR}]"

    def __init__(
        self,
        root_folder: str = None,
        storage_folder: str = None,
        clean_entities_enabled: Union[bool, str] = None,
        **properties,
    ):
        self.root_folder = root_folder
        self.storage_folder = storage_folder
        self.clean_entities_enabled = clean_entities_enabled
        self.properties = properties

    def __getattr__(self, item: str) -> Optional[Any]:
        return self.properties.get(item)

    @classmethod
    def default_config(cls) -> GlobalAppConfig:
        config = GlobalAppConfig()
        config.root_folder = cls._DEFAULT_ROOT_FOLDER
        config.storage_folder = cls._DEFAULT_STORAGE_FOLDER
        config.clean_entities_enabled = cls._CLEAN_ENTITIES_ENABLED_TEMPLATE
        return config

    def _to_dict(self):
        as_dict = {}
        if self.root_folder:
            as_dict[self._ROOT_FOLDER_KEY] = self.root_folder
        if self.storage_folder:
            as_dict[self._STORAGE_FOLDER_KEY] = self.storage_folder
        if self.clean_entities_enabled is not None:
            as_dict[self._CLEAN_ENTITIES_ENABLED_KEY] = self.clean_entities_enabled
        as_dict.update(self.properties)
        return as_dict

    @classmethod
    def _from_dict(cls, config_as_dict: Dict[str, Any]):
        config = GlobalAppConfig()
        config.root_folder = config_as_dict.pop(cls._ROOT_FOLDER_KEY, None)
        config.storage_folder = config_as_dict.pop(cls._STORAGE_FOLDER_KEY, None)
        config.clean_entities_enabled = config_as_dict.pop(cls._CLEAN_ENTITIES_ENABLED_KEY, None)
        config.properties = config_as_dict
        return config

    def _update(self, config_as_dict):
        self.root_folder = _tpl._replace_templates(config_as_dict.pop(self._ROOT_FOLDER_KEY, self.root_folder))
        self.storage_folder = _tpl._replace_templates(config_as_dict.pop(self._STORAGE_FOLDER_KEY, self.storage_folder))
        self.clean_entities_enabled = _tpl._replace_templates(
            config_as_dict.pop(self._CLEAN_ENTITIES_ENABLED_KEY, self.clean_entities_enabled),
            type=bool,
            required=False,
            default=self._DEFAULT_CLEAN_ENTITIES_ENABLED,
        )
        self.properties.update(config_as_dict)
        for k, v in self.properties.items():
            self.properties[k] = _tpl._replace_templates(v)
