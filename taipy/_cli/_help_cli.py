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

import sys

from taipy._cli._base_cli import _CLI
from taipy.logger._taipy_logger import _TaipyLogger


class _HelpCLI:
    __logger = _TaipyLogger._get_logger()

    @classmethod
    def create_parser(cls):
        create_parser = _CLI._add_subparser("help", help="Show the Taipy help message.", add_help=False)
        create_parser.add_argument(
            "command", nargs="?", type=str, const="", default="", help="Show the help message of the command."
        )

    @classmethod
    def parse_arguments(cls):
        args = _CLI._parse()

        if getattr(args, "which", None) == "help":
            if args.command:
                if args.command in _CLI._sub_taipyparsers.keys():
                    _CLI._sub_taipyparsers.get(args.command).print_help()
                else:
                    cls.__logger.error(f"{args.command} is not a valid command.")
            else:
                _CLI._parser.print_help()

            sys.exit(0)
