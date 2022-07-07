from abc import abstractmethod
from typing import Optional, Any, Dict

from .common._template_handler import _TemplateHandler as _tpl


class AbstractSubConfig:

    def __init__(self, **properties):
        self._properties = properties

    def __getattr__(self, item: str) -> Optional[Any]:
        return _tpl._replace_templates(self._properties.get(item))

    @abstractmethod
    def __copy__(self):
        raise NotImplemented

    def _replace_template(self, value):
        return _tpl._replace_templates(value)

    @property
    def properties(self):
        return {k: _tpl._replace_templates(v) for k, v in self._properties.items()}

    @properties.setter  # type: ignore
    def properties(self, val):
        self._properties = val

    @abstractmethod
    def default_config(cls):
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
