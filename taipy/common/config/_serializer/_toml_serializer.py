# Copyright 2021-2024 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import toml  # type: ignore

from .._config import _Config
from ..exceptions.exceptions import LoadingError
from ._base_serializer import _BaseSerializer


class _TomlSerializer(_BaseSerializer):
    """Convert configuration from TOML representation to Python Dict and reciprocally."""

    @classmethod
    def _write(cls, configuration: _Config, filename: str):
        with open(filename, "w") as fd:
            toml.dump(cls._str(configuration), fd)

    @classmethod
    def _read(cls, filename: str) -> _Config:
        try:
            config_as_dict = cls._pythonify(dict(toml.load(filename)))
            return cls._from_dict(config_as_dict)
        except toml.TomlDecodeError as e:
            error_msg = f"Can not load configuration {e}"
            raise LoadingError(error_msg) from None

    @classmethod
    def _serialize(cls, configuration: _Config) -> str:
        return toml.dumps(cls._str(configuration))

    @classmethod
    def _deserialize(cls, config_as_string: str) -> _Config:
        return cls._from_dict(cls._pythonify(dict(toml.loads(config_as_string))))
