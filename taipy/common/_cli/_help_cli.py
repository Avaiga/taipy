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

import sys

from ._base_cli._abstract_cli import _AbstractCLI
from ._base_cli._taipy_parser import _TaipyParser


class _HelpCLI(_AbstractCLI):
    _COMMAND_NAME = "help"

    @classmethod
    def create_parser(cls):
        create_parser = _TaipyParser._add_subparser(
            cls._COMMAND_NAME,
            help="Show the Taipy help message.",
            add_help=False,
        )
        create_parser.add_argument(
            "command", nargs="?", type=str, const="", default="", help="Show the help message of the command."
        )

    @classmethod
    def handle_command(cls):
        args = cls._parse_arguments()
        if not args:
            return

        if args.command:
            if args.command in _TaipyParser._sub_taipyparsers.keys():
                _TaipyParser._sub_taipyparsers.get(args.command).print_help()
            else:
                cls._logger.error(f"{args.command} is not a valid command.")
        else:
            _TaipyParser._parser.print_help()

        sys.exit(0)
