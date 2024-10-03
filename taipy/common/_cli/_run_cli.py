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
            "external-args",
            help="""
                Arguments defined after this keyword will be considered as external arguments
                to be passed to the application
            """,
        )

    @classmethod
    def handle_command(cls):
        args, _ = _TaipyParser._parser.parse_known_args()
        if getattr(args, "which", None) != "run":
            return

        # First 2 args are always (1) Python executable, (2) run
        # Unknown args are passed when running the application but will be ignored
        all_args = sys.argv[2:]

        external_args = []
        try:
            external_args_index = all_args.index("external-args")
        except ValueError:
            pass
        else:
            external_args.extend(all_args[external_args_index + 1 :])
            all_args = all_args[:external_args_index]

        taipy_args = [f"--taipy-{arg[2:]}" if arg.startswith("--") else arg for arg in all_args]

        try:
            subprocess.run(
                [sys.executable, args.application_main_file, *(external_args + taipy_args)],
                stdout=sys.stdout,
                stderr=sys.stdout,
            )
        except KeyboardInterrupt:
            pass

        sys.exit(0)
