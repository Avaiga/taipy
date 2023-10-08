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
from taipy.core._core_cli import _CoreCLI
from taipy.core._migrate_cli import _MigrateCLI
from taipy.core._version._cli._version_cli import _VersionCLI
from taipy.gui._gui_cli import _GuiCLI

from ._cli._help_cli import _HelpCLI
from ._cli._run_cli import _RunCLI
from ._cli._scaffold_cli import _ScaffoldCLI
from .version import _get_version


def _entrypoint():
    # Add the current working directory to path to execute version command on FS repo
    sys.path.append(os.path.normpath(os.getcwd()))

    _CLI._parser.add_argument("-v", "--version", action="store_true", help="Print the current Taipy version and exit.")

    _RunCLI.create_parser()
    _GuiCLI.create_run_parser()
    _CoreCLI.create_run_parser()

    _VersionCLI.create_parser()
    _ScaffoldCLI.create_parser()
    _MigrateCLI.create_parser()
    _HelpCLI.create_parser()

    args = _CLI._parse()
    if args.version:
        print(f"Taipy {_get_version()}")
        sys.exit(0)

    _RunCLI.parse_arguments()
    _HelpCLI.parse_arguments()
    _VersionCLI.parse_arguments()
    _MigrateCLI.parse_arguments()
    _ScaffoldCLI.parse_arguments()

    _CLI._remove_argument("help")
    _CLI._parser.print_help()
