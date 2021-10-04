from abc import abstractmethod
from typing import Dict


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
