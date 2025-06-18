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

from functools import lru_cache
from typing import Type

from ...common._modules import EnterpriseEdition
from .._manager._manager_factory import _ManagerFactory
from ..common._utils import _load_fct
from ._sequence_manager import _SequenceManager


class _SequenceManagerFactory(_ManagerFactory):
    @classmethod
    @lru_cache
    def _build_manager(cls) -> Type[_SequenceManager]:  # type: ignore
        if EnterpriseEdition._is_installed():
            sequence_manager = _load_fct(
                EnterpriseEdition._CORE_MODULE_PATH + ".sequence._sequence_manager", "_SequenceManager"
            )
        else:
            sequence_manager = _SequenceManager
        return sequence_manager  # type: ignore
