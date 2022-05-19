# Copyright 2022 Avaiga Private Limited
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

from taipy.core.common._validate_id import _validate_id
from taipy.core.common.scope import Scope
from taipy.core.config._config_template_handler import _ConfigTemplateHandler as _tpl


class DataNodeConfig:
    """
    Configuration fields needed to instantiate an actual `DataNode^` from the DataNodeConfig.

    A Data Node config is made to be used as a generator for actual data nodes. It holds configuration information
    needed to create an actual data node.

    Attributes:
        id (str):  Unique identifier of the data node config. It must be a valid Python variable name.
        storage_type (str): Storage type of the data nodes created from the data node config. The possible values
            are : "csv", "excel", "pickle", "sql", "generic" and "In_memory". The default value is "pickle".
            Note that the "in_memory" value can only be used when `JobConfig^`.mode is "standalone".
        scope (Scope^):  The `Scope^` of the data nodes instantiated from the data node config. The default value is
            SCENARIO.
        **properties: A dictionary of additional properties.
    """

    _STORAGE_TYPE_KEY = "storage_type"
    _STORAGE_TYPE_VALUE_PICKLE = "pickle"
    _STORAGE_TYPE_VALUE_SQL = "sql"
    _STORAGE_TYPE_VALUE_CSV = "csv"
    _STORAGE_TYPE_VALUE_EXCEL = "excel"
    _STORAGE_TYPE_VALUE_IN_MEMORY = "in_memory"
    _STORAGE_TYPE_VALUE_GENERIC = "generic"
    _DEFAULT_STORAGE_TYPE = _STORAGE_TYPE_VALUE_PICKLE

    _SCOPE_KEY = "scope"
    _DEFAULT_SCOPE = Scope.SCENARIO

    _IS_CACHEABLE_KEY = "cacheable"
    _DEFAULT_IS_CACHEABLE_VALUE = False

    def __init__(self, id: str, storage_type: str = None, scope: Scope = None, **properties):
        self.id = _validate_id(id)
        self._storage_type = storage_type
        self._scope = scope
        self._properties = properties
        if self._properties.get(self._IS_CACHEABLE_KEY) is None:
            self._properties[self._IS_CACHEABLE_KEY] = self._DEFAULT_IS_CACHEABLE_VALUE

    def __getattr__(self, item: str) -> Optional[Any]:
        return _tpl._replace_templates(self._properties.get(item))

    def __copy__(self):
        return DataNodeConfig(self.id, self._storage_type, self._scope, **copy(self._properties))

    @property
    def storage_type(self):
        return _tpl._replace_templates(self._storage_type)

    @storage_type.setter  # type: ignore
    def storage_type(self, val):
        self._storage_type = val

    @property
    def properties(self):
        return {k: _tpl._replace_templates(v) for k, v in self._properties.items()}

    @properties.setter  # type: ignore
    def properties(self, val):
        self._properties = val

    @property
    def scope(self):
        return _tpl._replace_templates(self._scope)

    @scope.setter  # type: ignore
    def scope(self, val):
        self._scope = val

    @classmethod
    def default_config(cls, id):
        return DataNodeConfig(id, cls._DEFAULT_STORAGE_TYPE, cls._DEFAULT_SCOPE)

    def _to_dict(self):
        as_dict = {}
        if self._storage_type is not None:
            as_dict[self._STORAGE_TYPE_KEY] = self._storage_type
        if self._scope is not None:
            as_dict[self._SCOPE_KEY] = self._scope
        as_dict.update(self._properties)
        return as_dict

    @classmethod
    def _from_dict(cls, id: str, config_as_dict: Dict[str, Any]):
        config = DataNodeConfig(id)
        config.id = _validate_id(id)
        config._storage_type = config_as_dict.pop(cls._STORAGE_TYPE_KEY, None)
        config._scope = config_as_dict.pop(cls._SCOPE_KEY, None)
        config._properties = config_as_dict
        return config

    def _update(self, config_as_dict, default_dn_cfg=None):
        self._storage_type = (
            config_as_dict.pop(self._STORAGE_TYPE_KEY, self._storage_type) or default_dn_cfg.storage_type
        )
        self._scope = config_as_dict.pop(self._SCOPE_KEY, self._scope) or default_dn_cfg.scope
        self._properties.update(config_as_dict)
        if default_dn_cfg:
            self._properties = {**default_dn_cfg.properties, **self._properties}
