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

from importlib import import_module, util
from operator import attrgetter
from typing import Type

from taipy._cli._base_cli._abstract_cli import _AbstractCLI

from ._core_cli import _CoreCLI


class _CoreCLIFactory:
    _TAIPY_ENTERPRISE_MODULE = "taipy.enterprise"
    _TAIPY_ENTERPRISE_CORE_MODULE = _TAIPY_ENTERPRISE_MODULE + ".core"

    @classmethod
    def _build_cli(cls) -> Type[_AbstractCLI]:
        if util.find_spec(cls._TAIPY_ENTERPRISE_MODULE) is not None:
            module = import_module(cls._TAIPY_ENTERPRISE_CORE_MODULE + "._cli._core_cli")
            core_cli = attrgetter("_CoreCLI")(module)
        else:
            core_cli = _CoreCLI

        return core_cli
