from copy import copy
from typing import Any, Dict, Optional, Union

from taipy.core.common.unicode_to_python_variable_name import protect_name
from taipy.core.config.config_template_handler import ConfigTemplateHandler as tpl
from taipy.core.data.scope import Scope


class DataNodeConfig:
    """
    Holds all the configuration fields needed to create actual data nodes from the DataNodeConfig.

    A Data Node config is made to be used as a generator for actual data nodes. It holds configuration information
    needed to create an actual data node.

    Attributes:
        id (str):  Unique identifier of the data node config.
            We strongly recommend to use lowercase alphanumeric characters, dash character '-', or underscore character
            '_'. Note that other characters are replaced according the following rules :
            - Space characters are replaced by underscore characters ('_').
            - Unicode characters are replaced by a corresponding alphanumeric character using the Unicode library.
            - Other characters are replaced by dash characters ('-').
        storage_type (str): Storage type of the data nodes created from the data node config. The possible values
            are : "csv", "excel", "pickle", "sql", "generic" and "In_memory". Default value is "pickle".
            Note that the "in_memory" value can only be used when JobConfig.mode is "standalone".
        scope (Scope):  The usage scope of the data nodes created from the data node config. Default value is
            Pipeline.
        properties (dict): Dictionary of additional properties.
    """

    STORAGE_TYPE_KEY = "storage_type"
    STORAGE_TYPE_VALUE_PICKLE = "pickle"
    STORAGE_TYPE_VALUE_SQL = "sql"
    STORAGE_TYPE_VALUE_CSV = "csv"
    STORAGE_TYPE_VALUE_EXCEL = "excel"
    STORAGE_TYPE_VALUE_IN_MEMORY = "in_memory"
    STORAGE_TYPE_VALUE_GENERIC = "generic"
    DEFAULT_STORAGE_TYPE = STORAGE_TYPE_VALUE_PICKLE

    SCOPE_KEY = "scope"
    DEFAULT_SCOPE = Scope.SCENARIO

    IS_CACHEABLE_KEY = "cacheable"
    DEFAULT_IS_CACHEABLE_VALUE = False

    def __init__(self, id: str, storage_type: str = None, scope: Scope = None, **properties):
        self.id = protect_name(id)
        self.storage_type = storage_type
        self.scope = scope
        self.properties = properties
        if self.properties.get(self.IS_CACHEABLE_KEY) is None:
            self.properties[self.IS_CACHEABLE_KEY] = self.DEFAULT_IS_CACHEABLE_VALUE

    def __getattr__(self, item: str) -> Optional[Any]:
        return self.properties.get(item)

    def __copy__(self):
        return DataNodeConfig(self.id, self.storage_type, self.scope, **copy(self.properties))

    @classmethod
    def default_config(cls, id):
        return DataNodeConfig(id, cls.DEFAULT_STORAGE_TYPE, cls.DEFAULT_SCOPE)

    def to_dict(self):
        as_dict = {}
        if self.storage_type is not None:
            as_dict[self.STORAGE_TYPE_KEY] = self.storage_type
        if self.scope is not None:
            as_dict[self.SCOPE_KEY] = self.scope
        as_dict.update(self.properties)
        return as_dict

    @classmethod
    def from_dict(cls, id: str, config_as_dict: Dict[str, Any]):
        config = DataNodeConfig(id)
        config.id = protect_name(id)
        config.storage_type = config_as_dict.pop(cls.STORAGE_TYPE_KEY, None)
        config.scope = config_as_dict.pop(cls.SCOPE_KEY, None)
        config.properties = config_as_dict
        return config

    def update(self, config_as_dict, default_dn_cfg=None):
        self.storage_type = config_as_dict.pop(self.STORAGE_TYPE_KEY, self.storage_type) or default_dn_cfg.storage_type
        self.storage_type = tpl.replace_templates(self.storage_type)
        self.scope = config_as_dict.pop(self.SCOPE_KEY, self.scope) or default_dn_cfg.scope
        self.scope = tpl.replace_templates(
            config_as_dict.pop(self.SCOPE_KEY, self.scope) or default_dn_cfg.scope, Scope
        )
        self.properties.update(config_as_dict)
        if default_dn_cfg:
            self.properties = {**default_dn_cfg.properties, **self.properties}
        for k, v in self.properties.items():
            self.properties[k] = tpl.replace_templates(v)
