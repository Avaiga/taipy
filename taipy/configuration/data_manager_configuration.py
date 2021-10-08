from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from .interface import Configurable


@dataclass
class DataManagerConfiguration(Configurable):
    default_node = "default"
    properties: Dict[str, Any] = field(default_factory=dict)
    default_properties: Dict[str, Any] = field(default_factory=dict)

    def __getitem__(self, node: str) -> Optional[Any]:
        return self.properties.get(node) or self.default_properties

    def update(self, config: Dict):
        self.default_properties = config.pop(self.default_node, self.default_properties)
        self.properties = config
        self.__add_default_values_to_properties()

    def export(self):
        return {self.default_node: self.default_properties, **self.properties}

    def __add_default_values_to_properties(self):
        for k, v in self.properties.items():
            self.properties[k] = {**self.default_properties, **v}
