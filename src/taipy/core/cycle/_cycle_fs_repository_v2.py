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
from .._repository._v2._filesystem_repository import _FileSystemRepository
from ._cycle_model import _CycleModel
from ._cycle_repository_mixin import _CycleRepositoryMixin
from .cycle import Cycle


class _CycleFSRepository(_FileSystemRepository[_CycleModel, Cycle], _CycleRepositoryMixin):
    def __init__(self):
        super().__init__(model=_CycleModel, dir_name="cycles")
