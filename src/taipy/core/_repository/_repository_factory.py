# Copyright 2022 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

from typing import Any, Optional, Union

from taipy.config import Config

from .._repository import _FileSystemRepository


class _RepositoryFactory:
    _REPOSITORY_MAP = {"default": _FileSystemRepository}

    @classmethod
    def build_repository(cls) -> Optional[Union[_FileSystemRepository, Any]]:
        repo = cls._REPOSITORY_MAP.get(Config.global_config.repository_type)

        if not repo:
            return cls._REPOSITORY_MAP.get("default")

        return repo
