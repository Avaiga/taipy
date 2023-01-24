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
import pathlib
from typing import Optional

from ._scenario_model import _ScenarioModel
from ._scenario_repository import _ScenarioRepository


class _ScenarioFSRepository(_ScenarioRepository):
    def __init__(self):
        super().__init__(model=_ScenarioModel, dir_name="scenarios")

    @property
    def dir_path(self):
        return super().repository.dir_path

    @property
    def _storage_folder(self) -> pathlib.Path:
        return super().repository._storage_folder

    def _get_by_config_and_owner_id(self, config_id: str, owner_id: Optional[str]):
        super().repository._get_by_config_and_owner_id(config_id, owner_id)

    def _get_by_configs_and_owner_ids(self, configs_and_owner_ids):
        return super().repository._get_by_configs_and_owner_ids(configs_and_owner_ids)

    def __match_file_and_get_entity(self, filepath, config_and_owner_ids, retry: Optional[int] = 0):
        super().repository.__match_file_and_get_entity(filepath, config_and_owner_ids, retry)
