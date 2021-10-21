from abc import abstractmethod
from typing import Any, Dict, Optional


class Configurable:
    """
    Element that can be configured from a Python Dict
    """

    @abstractmethod
    def update(self, configuration: Dict):
        """
        Allow to update each configuration of a configurable
        If a configuration is not present, the default is kept
        """
        ...

    @abstractmethod
    def export(self) -> Dict:
        """
        Return the current configuration
        """
        ...


class ConfigRepository:
    def __init__(self):
        self._data = {}

    @abstractmethod
    def create(self, *args, **kwargs):
        ...

    def get(self, item: str, default: Optional[Any] = None) -> Any:
        return self._data.get(item, default)

    def __getitem__(self, item: str):
        return self._data[item]

    def __iter__(self):
        yield from self._data.values()

    def __len__(self):
        return len(self._data)
