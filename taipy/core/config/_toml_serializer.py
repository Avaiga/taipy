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

from taipy.core.common._validate_id import _validate_id
from taipy.core.common.frequency import Frequency
from taipy.core.common.scope import Scope
from taipy.core.config._config import _Config
from taipy.core.config._config_template_handler import _ConfigTemplateHandler
from taipy.core.config.data_node_config import DataNodeConfig
from taipy.core.config.global_app_config import GlobalAppConfig
from taipy.core.config.job_config import JobConfig
from taipy.core.config.pipeline_config import PipelineConfig
from taipy.core.config.scenario_config import ScenarioConfig
from taipy.core.config.task_config import TaskConfig
from taipy.core.exceptions.exceptions import LoadingError


class _TomlSerializer:
    """Convert configuration from TOML representation to Python Dict and reciprocally."""

    _GLOBAL_NODE_NAME = "TAIPY"
    _JOB_NODE_NAME = "JOB"
    _DATA_NODE_NAME = "DATA_NODE"
    _TASK_NODE_NAME = "TASK"
    _PIPELINE_NODE_NAME = "PIPELINE"
    _SCENARIO_NODE_NAME = "SCENARIO"

    @classmethod
    def _write(cls, configuration: _Config, filename: str):
        config = {
            cls._GLOBAL_NODE_NAME: configuration._global_config._to_dict(),
            cls._JOB_NODE_NAME: configuration._job_config._to_dict(),
            cls._DATA_NODE_NAME: cls.__to_dict(configuration._data_nodes),
            cls._TASK_NODE_NAME: cls.__to_dict(configuration._tasks),
            cls._PIPELINE_NODE_NAME: cls.__to_dict(configuration._pipelines),
            cls._SCENARIO_NODE_NAME: cls.__to_dict(configuration._scenarios),
        }
        with open(filename, "w") as fd:
            toml.dump(cls.__stringify(config), fd)

    @classmethod
    def __to_dict(cls, dict_of_configs: Dict[str, Any]):
        return {key: value._to_dict() for key, value in dict_of_configs.items()}

    @classmethod
    def __stringify(cls, config):
        if config is None:
            return None
        if isinstance(config, Scope):
            return config.name
        if isinstance(config, Frequency):
            return config.name
        if isinstance(config, DataNodeConfig):
            return config.id
        if isinstance(config, TaskConfig):
            return config.id
        if isinstance(config, PipelineConfig):
            return config.id
        if isinstance(config, bool):
            return str(config) + ":bool"
        if isinstance(config, int):
            return str(config) + ":int"
        if isinstance(config, float):
            return str(config) + ":float"
        if isinstance(config, dict):
            return {str(key): cls.__stringify(val) for key, val in config.items()}
        if isinstance(config, list):
            return [cls.__stringify(val) for val in config]
        if isinstance(config, tuple):
            return [cls.__stringify(val) for val in config]
        return config

    @classmethod
    def _read(cls, filename: str) -> _Config:
        try:
            config_as_dict = cls._pythonify(dict(toml.load(filename)))
            return cls.__from_dict(config_as_dict)
        except toml.TomlDecodeError as e:
            error_msg = f"Can not load configuration {e}"
            raise LoadingError(error_msg)

    @staticmethod
    def _extract_node(config_as_dict, cls_config, node, config: Optional[dict]):
        res = {}
        for key, value in config_as_dict.get(node, {}).items():
            key = _validate_id(key)
            res[key] = (
                cls_config._from_dict(key, value) if config is None else cls_config._from_dict(key, value, config)
            )
        return res

    @classmethod
    def __from_dict(cls, config_as_dict) -> _Config:
        config = _Config()
        config._global_config = GlobalAppConfig._from_dict(config_as_dict.get(cls._GLOBAL_NODE_NAME, {}))
        config._job_config = JobConfig._from_dict(config_as_dict.get(cls._JOB_NODE_NAME, {}))
        config._data_nodes = cls._extract_node(config_as_dict, DataNodeConfig, cls._DATA_NODE_NAME, None)
        config._tasks = cls._extract_node(config_as_dict, TaskConfig, cls._TASK_NODE_NAME, config._data_nodes)
        config._pipelines = cls._extract_node(config_as_dict, PipelineConfig, cls._PIPELINE_NODE_NAME, config._tasks)
        config._scenarios = cls._extract_node(
            config_as_dict, ScenarioConfig, cls._SCENARIO_NODE_NAME, config._pipelines
        )
        return config

    @classmethod
    def _pythonify(cls, val):
        match = re.fullmatch(_ConfigTemplateHandler._PATTERN, str(val))
        if not match:
            if isinstance(val, str):
                TYPE_PATTERN = r"^(.+):(\bbool\b|\bstr\b|\bfloat\b|\bint\b)?$"
                match = re.fullmatch(TYPE_PATTERN, str(val))
                if match:
                    actual_val = match.group(1)
                    dynamic_type = match.group(2)
                    if dynamic_type == "bool":
                        return _ConfigTemplateHandler._to_bool(actual_val)
                    elif dynamic_type == "int":
                        return _ConfigTemplateHandler._to_int(actual_val)
                    elif dynamic_type == "float":
                        return _ConfigTemplateHandler._to_float(actual_val)
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
