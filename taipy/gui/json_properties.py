# Copyright 2021-2025 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import typing as t
from abc import ABC, abstractmethod
from dataclasses import dataclass


class JsonableProperty(ABC):
    # Support for making the class JSON-serializable
    @abstractmethod
    def to_jsonable(self) -> t.Any:  # TODO: better type hint for return type
        raise NotImplementedError()


class JsonProperty(ABC):
    # Raw JSON string property, used when the property value is already a JSON string and should
    # not be further serialized
    @abstractmethod
    def to_json(self) -> str:
        raise NotImplementedError()


@dataclass
# Configuration for chart animations
class ChartAnimation(JsonableProperty):
    # List of columns to animate
    columns: list[str]
    # Easing function to use for the animation
    easing: str = "linear"
    # Duration of the animation in milliseconds
    duration: int = 500

    def to_jsonable(self) -> dict:
        return {
            "columns": self.columns,
            "easing": self.easing,
            "duration": self.duration,
        }
