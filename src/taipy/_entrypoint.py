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

import os
import sys

from taipy._cli._base_cli import _CLI
from taipy.core._version._cli._version_cli import _VersionCLI

from ._cli._help_cli import _HelpCLI
from ._cli._scaffold_cli import _ScaffoldCLI


def _entrypoint():
    # Add the current working directory to path to execute version command on FS repo
    sys.path.append(os.path.normpath(os.getcwd()))

    _VersionCLI.create_parser()
    _ScaffoldCLI.create_parser()
    _HelpCLI.create_parser()

    _HelpCLI.parse_arguments()
    _VersionCLI.parse_arguments()
    _ScaffoldCLI.parse_arguments()

    _CLI._remove_argument("help")
    _CLI._parser.print_help()
