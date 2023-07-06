# Copyright 2023 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

from datetime import datetime
from typing import Any

from taipy.config import Config
from taipy.config._config import _Config

from .._entity._entity import _Entity


class _Version(_Entity):
    def __init__(self, id: str, config: Any) -> None:
        self.id: str = id
        self.config: _Config = config
        self.creation_date: datetime = datetime.now()

    def __eq__(self, other):
        return self.id == other.id and self.__is_config_eq(other)

    def __is_config_eq(self, other):
        return Config._serializer._str(self.config) == Config._serializer._str(other.config)
