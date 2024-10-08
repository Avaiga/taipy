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

import subprocess
import sys

from ._base_cli._abstract_cli import _AbstractCLI
from ._base_cli._taipy_parser import _TaipyParser


class _RunCLI(_AbstractCLI):
    _COMMAND_NAME = "run"

    @classmethod
    def create_parser(cls):
        run_parser = _TaipyParser._add_subparser(cls._COMMAND_NAME, help="Run a Taipy application.")
        run_parser.add_argument(
            "application_main_file",
        )

        sub_run_parser = run_parser.add_subparsers(title="subcommands")
        sub_run_parser.add_parser(
            "external-arguments",
            help="""
                Arguments defined after this keyword will be considered as external arguments
                to be passed to the application
            """,
        )

    @classmethod
    def handle_command(cls):
        arguments, _ = _TaipyParser._parser.parse_known_arguments()
        if getattr(arguments, "which", None) != "run":
            return

        # First 2 arguments are always (1) Python executable, (2) run
        # Unknown arguments are passed when running the application but will be ignored
        all_arguments = sys.argv[2:]

        external_arguments = []
        try:
            external_arguments_index = all_arguments.index("external-arguments")
        except ValueError:
            pass
        else:
            external_arguments.extend(all_arguments[external_arguments_index + 1 :])
            all_arguments = all_arguments[:external_arguments_index]

        taipy_arguments = [f"--taipy-{arg[2:]}" if arg.startswith("--") else arg for arg in all_arguments]

        try:
            subprocess.run(
                [sys.executable, arguments.application_main_file, *(external_arguments + taipy_arguments)],
                stdout=sys.stdout,
                stderr=sys.stdout,
            )
        except KeyboardInterrupt:
            pass

        sys.exit(0)
