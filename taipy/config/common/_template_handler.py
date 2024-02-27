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
import re
from collections import UserDict
from datetime import datetime, timedelta
from importlib import import_module
from operator import attrgetter
from pydoc import locate

from ..exceptions.exceptions import InconsistentEnvVariableError, MissingEnvVariableError
from .frequency import Frequency
from .scope import Scope


class _TemplateHandler:
    """Factory to handle actions related to config value templating."""

    _PATTERN = r"^ENV\[([a-zA-Z_]\w*)\](:(\bbool\b|\bstr\b|\bfloat\b|\bint\b))?$"

    @classmethod
    def _replace_templates(cls, template, type=str, required=True, default=None):
        if isinstance(template, tuple):
            return tuple(cls._replace_template(item, type, required, default) for item in template)
        if isinstance(template, list):
            return [cls._replace_template(item, type, required, default) for item in template]
        if isinstance(template, dict):
            return {str(k): cls._replace_template(v, type, required, default) for k, v in template.items()}
        if isinstance(template, UserDict):
            return {str(k): cls._replace_template(v, type, required, default) for k, v in template.items()}
        return cls._replace_template(template, type, required, default)

    @classmethod
    def _replace_template(cls, template, type, required, default):
        if "ENV" not in str(template):
            return template
        if match := re.fullmatch(cls._PATTERN, str(template)):
            var = match.group(1)
            dynamic_type = match.group(3)
            val = os.environ.get(var)
            if val is None:
                if required:
                    raise MissingEnvVariableError(f"Environment variable {var} is not set.")
                return default
            if type == bool:
                return cls._to_bool(val)
            elif type == int:
                return cls._to_int(val)
            elif type == float:
                return cls._to_float(val)
            elif type == Scope:
                return cls._to_scope(val)
            elif type == Frequency:
                return cls._to_frequency(val)
            else:
                if dynamic_type == "bool":
                    return cls._to_bool(val)
                elif dynamic_type == "int":
                    return cls._to_int(val)
                elif dynamic_type == "float":
                    return cls._to_float(val)
                return val
        return template

    @staticmethod
    def _to_bool(val: str) -> bool:
        possible_values = ["true", "false"]
        if str.lower(val) not in possible_values:
            raise InconsistentEnvVariableError("{val} is not a Boolean.")
        return str.lower(val) == "true" or str.lower(val) != "false"

    @staticmethod
    def _to_int(val: str) -> int:
        try:
            return int(val)
        except ValueError:
            raise InconsistentEnvVariableError(f"{val} is not an integer.") from None

    @staticmethod
    def _to_float(val: str) -> float:
        try:
            return float(val)
        except ValueError:
            raise InconsistentEnvVariableError(f"{val} is not a float.") from None

    @staticmethod
    def _to_datetime(val: str) -> datetime:
        try:
            return datetime.fromisoformat(val)
        except ValueError:
            raise InconsistentEnvVariableError(f"{val} is not a valid datetime.") from None

    @staticmethod
    def _to_timedelta(val: str) -> timedelta:
        """
        Parse a time string e.g. (2h13m) into a timedelta object.

        :param timedelta_str: A string identifying a duration.  (eg. 2h13m)
        :return datetime.timedelta: A datetime.timedelta object
        """
        regex = re.compile(
            r"^((?P<days>[\.\d]+?)d)? *"
            r"((?P<hours>[\.\d]+?)h)? *"
            r"((?P<minutes>[\.\d]+?)m)? *"
            r"((?P<seconds>[\.\d]+?)s)?$"
        )
        parts = regex.match(val)
        if not parts:
            raise InconsistentEnvVariableError(f"{val} is not a valid timedelta.")
        time_params = {name: float(param) for name, param in parts.groupdict().items() if param}
        return timedelta(**time_params)  # type: ignore

    @staticmethod
    def _to_scope(val: str) -> Scope:
        try:
            return Scope[str.upper(val)]
        except Exception:
            raise InconsistentEnvVariableError(f"{val} is not a valid scope.") from None

    @staticmethod
    def _to_frequency(val: str) -> Frequency:
        try:
            return Frequency[str.upper(val)]
        except Exception:
            raise InconsistentEnvVariableError(f"{val} is not a valid frequency.") from None

    @staticmethod
    def _to_function(val: str):
        module_name, fct_name = val.rsplit(".", 1)
        try:
            module = import_module(module_name)
            return attrgetter(fct_name)(module)
        except Exception:
            raise InconsistentEnvVariableError(f"{val} is not a valid function.") from None

    @staticmethod
    def _to_class(val: str):
        try:
            return locate(val)
        except Exception:
            raise InconsistentEnvVariableError(f"{val} is not a valid class.") from None
