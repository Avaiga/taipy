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
from taipy.core import Orchestrator
from .version import _get_version

orchestrator = Orchestrator()
orchestrator.run()

gui = Gui()
gui_args = _GuiCLI.handle_command()
gui.run(run_server=True, **vars(gui_args))

rest = Rest()
rest.run()
