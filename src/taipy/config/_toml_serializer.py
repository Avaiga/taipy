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

import re
from typing import Any, Dict, Optional

import toml  # type: ignore

from . import Section
# from .job_execution.job_config import JobConfig
# from .data_node.data_node_config import DataNodeConfig
# from .task.task_config import TaskConfig
# from .pipeline.pipeline_config import PipelineConfig
# from .scenario.scenario_config import ScenarioConfig
from ._config import _Config
from .common._template_handler import _TemplateHandler
from .common._validate_id import _validate_id
from .common.frequency import Frequency
from .common.scope import Scope
from .exceptions.exceptions import LoadingError
from .global_app.global_app_config import GlobalAppConfig
from .unique_section import UniqueSection


class _TomlSerializer:
    """Convert configuration from TOML representation to Python Dict and reciprocally."""

    _GLOBAL_NODE_NAME = "TAIPY"
    _section_class = {_GLOBAL_NODE_NAME: GlobalAppConfig}

    @classmethod
    def _write(cls, configuration: _Config, filename: str):
        with open(filename, "w") as fd:
            toml.dump(cls.__str(configuration), fd)

    @classmethod
    def __str(cls, configuration: _Config):
        config_as_dict = {cls._GLOBAL_NODE_NAME: configuration._global_config._to_dict()}
        for u_sect_name, u_sect in configuration._unique_sections.items():
            config_as_dict[u_sect_name] = u_sect._to_dict()
        for sect_name, sections in configuration._sections.items():
            config_as_dict[sect_name] = cls.__to_dict(sections)
        return cls.__stringify(config_as_dict)

    @classmethod
    def __to_dict(cls, sections: Dict[str, Any]):
        return {section_id: section._to_dict() for section_id, section in sections.items()}

    @classmethod
    def __stringify(cls, as_dict):
        if as_dict is None:
            return None
        if isinstance(as_dict, Section):
            return as_dict.id + ":SECTION"
        if isinstance(as_dict, Scope):
            return as_dict.name + ":SCOPE"
        if isinstance(as_dict, Frequency):
            return as_dict.name + ":FREQUENCY"
        if isinstance(as_dict, bool):
            return str(as_dict) + ":bool"
        if isinstance(as_dict, int):
            return str(as_dict) + ":int"
        if isinstance(as_dict, float):
            return str(as_dict) + ":float"
        if isinstance(as_dict, dict):
            return {str(key): cls.__stringify(val) for key, val in as_dict.items()}
        if isinstance(as_dict, list):
            return [cls.__stringify(val) for val in as_dict]
        if isinstance(as_dict, tuple):
            return [cls.__stringify(val) for val in as_dict]
        return as_dict

    @classmethod
    def _read(cls, filename: str) -> _Config:
        try:
            config_as_dict = cls._pythonify(dict(toml.load(filename)))
            return cls.__from_dict(config_as_dict)
        except toml.TomlDecodeError as e:
            error_msg = f"Can not load configuration {e}"
            raise LoadingError(error_msg)

    @classmethod
    def _serialize(cls, configuration: _Config) -> str:
        return toml.dumps(cls.__str(configuration))

    @classmethod
    def _deserialize(cls, config_as_string: str) -> _Config:
        return cls.__from_dict(cls._pythonify(dict(toml.loads(config_as_string))))

    @staticmethod
    def __extract_node(config_as_dict, cls_config, node, config: Optional[dict]) -> Dict[str, Section]:
        res = {}
        for key, value in config_as_dict.get(node, {}).items(): # my_task, {input=[], output=[my_data_node], ...}
            key = _validate_id(key)
            res[key] = cls_config._from_dict(value, key, config) # if config is None else cls_config._from_dict(key,
            # value, config)
        return res

    @classmethod
    def __from_dict(cls, as_dict) -> _Config:
        config = _Config()
        config._global_config = GlobalAppConfig._from_dict(as_dict.get(cls._GLOBAL_NODE_NAME, {}))
        for section_name, sect_as_dict in as_dict.items():
            if section_class := cls._section_class.get(section_name, None):
                if issubclass(section_class, UniqueSection):
                    config._unique_sections[section_name] = section_class._from_dict(sect_as_dict, None)
                elif issubclass(section_class, Section):
                    config._sections[section_name] = cls.__extract_node(as_dict, section_class, section_name, config)
        return config

    @classmethod
    def _pythonify(cls, val):
        match = re.fullmatch(_TemplateHandler._PATTERN, str(val))
        if not match:
            if isinstance(val, str):
                TYPE_PATTERN = r"^(.+):(\bbool\b|\bstr\b|\bfloat\b|\bint\b|\bSCOPE\b|\bFREQUENCY\b|\bSECTION\b)?$"
                match = re.fullmatch(TYPE_PATTERN, str(val))
                if match:
                    actual_val = match.group(1)
                    dynamic_type = match.group(2)
                    if dynamic_type == "SECTION":
                        return actual_val
                    if dynamic_type == "FREQUENCY":
                        return Frequency[actual_val]
                    if dynamic_type == "SCOPE":
                        return Scope[actual_val]
                    if dynamic_type == "bool":
                        return _TemplateHandler._to_bool(actual_val)
                    elif dynamic_type == "int":
                        return _TemplateHandler._to_int(actual_val)
                    elif dynamic_type == "float":
                        return _TemplateHandler._to_float(actual_val)
                    elif dynamic_type == "str":
                        return actual_val
                    else:
                        error_msg = f"Error loading toml configuration at {val}. {dynamic_type} type is not supported."
                        raise LoadingError(error_msg)
            if isinstance(val, dict):
                return {str(k): cls._pythonify(v) for k, v in val.items()}
            if isinstance(val, list):
                return [cls._pythonify(v) for v in val]
        return val
