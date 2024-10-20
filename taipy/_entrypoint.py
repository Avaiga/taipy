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

import os
import sys
from importlib.util import find_spec
from taipy.common.config import Config
from taipy.common._cli._base_cli._taipy_parser import _TaipyParser
from taipy.common._cli._create_cli import _CreateCLI
from taipy.config import Config
from taipy.common._cli._help_cli import _HelpCLI
from taipy.common._cli._run_cli import _RunCLI
from taipy.core._cli._core_cli_factory import _CoreCLIFactory
from taipy.core._entity._migrate_cli import _MigrateCLI
from taipy.core._version._cli._version_cli_factory import _VersionCLIFactory
from taipy.gui._gui_cli import _GuiCLI
from taipy.rest.rest_config import RestSection, configure_rest  
from taipy.gui import Gui
from taipy.rest import Rest
from taipy.core import Orchestrator
from .version import _get_version

def _entrypoint():
    _TaipyParser._parser.add_argument("--version", action="version", version=f"%(prog)s {_get_version()}")

    _CreateCLI.create_parser()
    _HelpCLI.create_parser()
    _RunCLI.create_parser()
    _MigrateCLI.create_parser()
    _VersionCLIFactory._build_cli().create_parser()
    _CoreCLIFactory._build_cli().create_parser()
    _GuiCLI.create_parser()

    # Add REST CLI options
    rest_group = _TaipyParser._add_groupparser("Taipy REST", "Optional arguments for Taipy REST service")
    rest_group.add_argument("--rest-port", type=int, help="Port to run the REST server on")
    rest_group.add_argument("--rest-host", type=str, help="Host to run the REST server on")
    rest_group.add_argument("--rest-use-https", action="store_true", help="Use HTTPS for REST server")
    rest_group.add_argument("--rest-ssl-cert", type=str, help="Path to SSL certificate for REST server")
    rest_group.add_argument("--rest-ssl-key", type=str, help="Path to SSL key for REST server")

    args = _TaipyParser._parser.parse_args()

    if hasattr(args, "which"):
        if args.which == _CreateCLI._COMMAND_NAME:
            _CreateCLI.handle_command()
        elif args.which == _HelpCLI._COMMAND_NAME:
            _HelpCLI.handle_command()
        elif args.which == _RunCLI._COMMAND_NAME:
            _RunCLI.handle_command()
        elif args.which == _MigrateCLI._COMMAND_NAME:
            _MigrateCLI.handle_command()
        elif args.which == _VersionCLIFactory._build_cli()._COMMAND_NAME:
            _VersionCLIFactory._build_cli().handle_command()
    else:
        _TaipyParser._parser.print_help()

def main():
    gui = Gui()
    gui_args = _GuiCLI.handle_command()
    gui.run(run_server=True, **vars(gui_args))

if __name__ == "__main__":
    _entrypoint()
