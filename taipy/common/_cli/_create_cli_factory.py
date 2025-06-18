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

from importlib import import_module
from operator import attrgetter
from typing import Type

from taipy.common._cli._base_cli._abstract_cli import _AbstractCLI

from .._modules import EnterpriseEdition
from ._create_cli import _CreateCLI


class _CreateCLIFactory:
    @staticmethod
    def _build_cli() -> Type[_AbstractCLI]:
        if EnterpriseEdition._is_installed():
            module = import_module(EnterpriseEdition._MODULE_PATH + ".templates._create_cli")
            create_cli = attrgetter("_CreateCLI")(module)
        else:
            create_cli = _CreateCLI

        return create_cli
