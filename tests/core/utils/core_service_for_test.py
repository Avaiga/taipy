# Copyright 2022 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

from click.testing import CliRunner

from src.taipy.core import Core
from src.taipy.core._scheduler._scheduler_factory import _SchedulerFactory
from src.taipy.core._version._version_cli import version_cli


class CoreForTest(Core):
    def __init__(self):
        self.runner = CliRunner()
        super().__init__()

    def run(self, parameters=[], force_restart=False):
        """
        Start a Core service. This method is blocking.
        """
        result = self.runner.invoke(version_cli, parameters, standalone_mode=False)
        cli_args = result.return_value

        self._Core__setup_versioning_module(*cli_args)

        if dispatcher := _SchedulerFactory._build_dispatcher(force_restart=force_restart):
            self._dispatcher = dispatcher
