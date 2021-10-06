from dataclasses import dataclass, field
from typing import Optional

from .interface import Configurable


@dataclass
class DataManagerConfiguration(Configurable):
    _path: str = field(default="")
    _type: str = field(default="")

    @property
    def path(self) -> Optional[str]:
        return self._path or None

    @property
    def type(self) -> Optional[str]:
        return self._type or None

    def update(self, config):
        self._path = config.get("path", self._path)
        self._type = config.get("type", self._type)

    def export(self):
        return {
            "path": self._path,
            "type": self._type,
        }
