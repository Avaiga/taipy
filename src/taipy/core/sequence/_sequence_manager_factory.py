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

from typing import Type

from .._manager._manager_factory import _ManagerFactory
from ..common._utils import _load_fct
from ._sequence_manager import _SequenceManager


class _SequenceManagerFactory(_ManagerFactory):
    @classmethod
    def _build_manager(cls) -> Type[_SequenceManager]:  # type: ignore
        if cls._using_enterprise():
            sequence_manager = _load_fct(
                cls._TAIPY_ENTERPRISE_CORE_MODULE + ".sequence._sequence_manager", "_SequenceManager"
            )  # type: ignore
        else:
            sequence_manager = _SequenceManager
        return sequence_manager  # type: ignore
