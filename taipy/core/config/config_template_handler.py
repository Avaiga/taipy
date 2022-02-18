import os
import re

from taipy.core.data.scope import Scope
from taipy.core.exceptions.configuration import InconsistentEnvVariableError, MissingEnvVariableError


class ConfigTemplateHandler:
    """Factory to handle actions related to config value templating."""

    PATTERN = r"^ENV\[([a-zA-Z_]\w*)\]$"

    @classmethod
    def replace_templates(cls, template, type=str):
        match = re.fullmatch(cls.PATTERN, str(template))
        if match:
            var = match.group(1)
            val = os.environ.get(var)
            if val is None:
                raise MissingEnvVariableError()
            if type == bool:
                return cls.to_bool(val)
            elif type == int:
                return cls.to_int(val)
            elif type == Scope:
                return cls.to_scope(val)
            else:
                return val
        return template

    @staticmethod
    def to_bool(val: str) -> bool:
        possible_values = ["true", "false"]
        if str.lower(val) not in possible_values:
            raise InconsistentEnvVariableError()
        return str.lower(val) == "true" or not (str.lower(val) == "false")

    @staticmethod
    def to_int(val: str) -> int:
        try:
            return int(val)
        except ValueError:
            raise InconsistentEnvVariableError()

    @staticmethod
    def to_scope(val: str) -> Scope:
        try:
            return Scope[str.upper(val)]
        except Exception:
            raise InconsistentEnvVariableError()
