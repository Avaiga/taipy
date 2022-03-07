from typing import Any, Dict, Optional, Union

from taipy.core.config.config_template_handler import ConfigTemplateHandler as tpl


class GlobalAppConfig:
    """
    Configuration fields related to the global application.

    Parameters:
        root_folder (str): Path of the base folder for the taipy application. The default value is "./taipy/"
        storage_folder (str): Folder name used to store Taipy data. The default value is ".data/". It is used in
            conjunction with the _root_folder_ field. That means the storage path is
            <root_folder><storage_folder> (The Default path : "./taipy/.data/")
        clean_entities_enabled (bool): Boolean field to activate/deactivate the clean entities feature. Default: false
        properties (dict): Dictionary of additional properties.
    """

    ROOT_FOLDER_KEY = "root_folder"
    DEFAULT_ROOT_FOLDER = "./taipy/"

    STORAGE_FOLDER_KEY = "storage_folder"
    DEFAULT_STORAGE_FOLDER = ".data/"

    CLEAN_ENTITIES_ENABLED_KEY = "clean_entities_enabled"
    CLEAN_ENTITIES_ENABLED_VALUE_TRUE = True
    CLEAN_ENTITIES_ENABLED_VALUE_FALSE = False
    DEFAULT_CLEAN_ENTITIES_ENABLED = CLEAN_ENTITIES_ENABLED_VALUE_FALSE

    def __init__(
        self,
        root_folder: str = None,
        storage_folder: str = None,
        clean_entities_enabled: Union[bool, str] = None,
        **properties
    ):
        self.root_folder = root_folder
        self.storage_folder = storage_folder
        self.clean_entities_enabled = clean_entities_enabled
        self.properties = properties

    def __getattr__(self, item: str) -> Optional[Any]:
        return self.properties.get(item)

    @classmethod
    def default_config(cls):
        config = GlobalAppConfig()
        config.root_folder = cls.DEFAULT_ROOT_FOLDER
        config.storage_folder = cls.DEFAULT_STORAGE_FOLDER
        config.clean_entities_enabled = cls.DEFAULT_CLEAN_ENTITIES_ENABLED
        return config

    def to_dict(self):
        as_dict = {}
        if self.root_folder:
            as_dict[self.ROOT_FOLDER_KEY] = self.root_folder
        if self.storage_folder:
            as_dict[self.STORAGE_FOLDER_KEY] = self.storage_folder
        if self.clean_entities_enabled is not None:
            as_dict[self.CLEAN_ENTITIES_ENABLED_KEY] = self.clean_entities_enabled
        as_dict.update(self.properties)
        return as_dict

    @classmethod
    def from_dict(cls, config_as_dict: Dict[str, Any]):
        config = GlobalAppConfig()
        config.root_folder = config_as_dict.pop(cls.ROOT_FOLDER_KEY, None)
        config.storage_folder = config_as_dict.pop(cls.STORAGE_FOLDER_KEY, None)
        config.clean_entities_enabled = config_as_dict.pop(cls.CLEAN_ENTITIES_ENABLED_KEY, None)
        config.properties = config_as_dict
        return config

    def update(self, config_as_dict):
        self.root_folder = tpl.replace_templates(config_as_dict.pop(self.ROOT_FOLDER_KEY, self.root_folder))
        self.storage_folder = tpl.replace_templates(config_as_dict.pop(self.STORAGE_FOLDER_KEY, self.storage_folder))
        self.clean_entities_enabled = tpl.replace_templates(
            config_as_dict.pop(self.CLEAN_ENTITIES_ENABLED_KEY, self.clean_entities_enabled), bool
        )
        self.properties.update(config_as_dict)
        for k, v in self.properties.items():
            self.properties[k] = tpl.replace_templates(v)
