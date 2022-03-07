import os
import re

from taipy.core.common.frequency import Frequency
from taipy.core.data.scope import Scope
from taipy.core.exceptions.configuration import InconsistentEnvVariableError, MissingEnvVariableError


class _ConfigTemplateHandler:
    """Factory to handle actions related to config value templating."""

    _PATTERN = r"^ENV\[([a-zA-Z_]\w*)\]$"

    @classmethod
    def _replace_templates(cls, template, type=str):
        match = re.fullmatch(cls._PATTERN, str(template))
        if match:
            var = match.group(1)
            val = os.environ.get(var)
            if val is None:
                raise MissingEnvVariableError()
            if type == bool:
                return cls._to_bool(val)
            elif type == int:
                return cls._to_int(val)
            elif type == Scope:
                return cls._to_scope(val)
            elif type == Frequency:
                return cls._to_frequency(val)
            else:
                return val
        return template

    @staticmethod
    def _to_bool(val: str) -> bool:
        possible_values = ["true", "false"]
        if str.lower(val) not in possible_values:
            raise InconsistentEnvVariableError()
        return str.lower(val) == "true" or not (str.lower(val) == "false")

    @staticmethod
    def _to_int(val: str) -> int:
        try:
            return int(val)
        except ValueError:
            raise InconsistentEnvVariableError()

    @staticmethod
    def _to_scope(val: str) -> Scope:
        try:
            return Scope[str.upper(val)]
        except Exception:
            raise InconsistentEnvVariableError()

    @staticmethod
    def _to_frequency(val: str) -> Frequency:
        try:
            return Frequency[str.upper(val)]
        except Exception:
            raise InconsistentEnvVariableError()
