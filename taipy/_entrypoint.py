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
import argparse
from importlib.util import find_spec
from taipy.common.config import Config
from taipy.common._cli._base_cli._taipy_parser import _TaipyParser
from taipy.common._cli._create_cli import _CreateCLI
from taipy.common._cli._help_cli import _HelpCLI
from taipy.common._cli._run_cli import _RunCLI
from taipy.core._cli._core_cli_factory import _CoreCLIFactory
from taipy.core._entity._migrate_cli import _MigrateCLI
from taipy.core._version._cli._version_cli_factory import _VersionCLIFactory
from taipy.gui._gui_cli import _GuiCLI
from taipy.rest.rest_config import RestSection, configure_rest  
from taipy.gui import Gui
from taipy.rest import Rest
from taipy.config import Config
from taipy.core import Orchestrator
from .version import _get_version


def parse_args():
    parser = argparse.ArgumentParser(description="Taipy server")
    # REST server arguments
    parser.add_argument("--rest-port", type=int, help="Port to run the REST server on")
    parser.add_argument("--rest-host", type=str, help="Host to run the REST server on")
    parser.add_argument("--rest-use-https", action="store_true", help="Use HTTPS for REST server")
    parser.add_argument("--rest-ssl-cert", type=str, help="Path to SSL certificate for REST server")
    parser.add_argument("--rest-ssl-key", type=str, help="Path to SSL key for REST server")
    return parser.parse_args()

def main():
    gui = Gui()

    gui_args = _GuiCLI.handle_command()

    gui.run(
        run_server=True,
        **vars(gui_args)  
    )

if __name__ == "__main__":
    # Initialize and run Taipy Core
    orchestrator = Orchestrator()
    orchestrator.run()

    # Configure REST
    rest_config = {
        "port": 5000,
        "host": "127.0.0.1",
        "use_https": False,
        "ssl_cert": None,
        "ssl_key": None
    }
    rest = Rest()

    # Run the REST service
    rest.run(**rest_config)

