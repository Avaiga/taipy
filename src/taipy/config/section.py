from abc import abstractmethod
from typing import Any, Dict, Optional

from .common._template_handler import _TemplateHandler as _tpl


class Section:

    def __init__(self, **properties):
        register = properties.pop("register", True)
        self._properties = properties
        if register:
            from .config import Config

            Config._register(self)

    @abstractmethod
    def __copy__(self):
        raise NotImplemented

    @property
    @abstractmethod
    def name(self):
        raise NotImplemented

    @abstractmethod
    def _to_dict(self):
        raise NotImplemented

    @classmethod
    @abstractmethod
    def _from_dict(cls, config_as_dict: Dict[str, Any]):
        raise NotImplemented

    @abstractmethod
    def _update(self, config_as_dict):
        raise NotImplemented

    def __getattr__(self, item: str) -> Optional[Any]:
        return self._replace_templates(self._properties.get(item, None))

    @property
    def properties(self):
        return {k: _tpl._replace_templates(v) for k, v in self._properties.items()}

    @properties.setter  # type: ignore
    def properties(self, val):
        self._properties = val

    def _replace_templates(self, value):
        return _tpl._replace_templates(value)
