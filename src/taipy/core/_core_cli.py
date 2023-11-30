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

from typing import Dict

from taipy._cli._base_cli import _CLI

from .config import CoreSection


class _CoreCLI:
    """Command-line interface for Taipy Core application."""

    __MODE_ARGS: Dict[str, Dict] = {
        "--development": {
            "action": "store_true",
            "dest": "taipy_development",
            "help": """
                When execute Taipy application in `development` mode, all entities from the previous development version
                will be deleted before running new Taipy application.
            """,
        },
        "--experiment": {
            "dest": "taipy_experiment",
            "nargs": "?",
            "const": "",
            "metavar": "VERSION",
            "help": """
                When execute Taipy application in `experiment` mode, the current Taipy application is saved to a new
                version. If version name already exists, check for compatibility with current Python Config and run the
                application. Without being specified, the version number will be a random string.
            """,
        },
        "--production": {
            "dest": "taipy_production",
            "nargs": "?",
            "const": "",
            "metavar": "VERSION",
            "help": """
                When execute in `production` mode, the current version is used in production. All production versions
                should have the same configuration and share all entities. Without being specified, the latest version
                is used.
            """,
        },
    }

    __FORCE_ARGS: Dict[str, Dict] = {
        "--force": {
            "dest": "taipy_force",
            "action": "store_true",
            "help": """
                Force override the configuration of the version if existed and run the application. Default to False.
            """,
        },
        "--no-force": {
            "dest": "no_taipy_force",
            "action": "store_true",
            "help": "Stop the application if any Config conflict exists.",
        },
    }

    @classmethod
    def create_parser(cls):
        core_parser = _CLI._add_groupparser("Taipy Core", "Optional arguments for Taipy Core service")

        mode_group = core_parser.add_mutually_exclusive_group()
        for mode_arg, mode_arg_dict in cls.__MODE_ARGS.items():
            mode_group.add_argument(mode_arg, cls.__add_taipy_prefix(mode_arg), **mode_arg_dict)

        force_group = core_parser.add_mutually_exclusive_group()
        for force_arg, force_arg_dict in cls.__FORCE_ARGS.items():
            force_group.add_argument(cls.__add_taipy_prefix(force_arg), **force_arg_dict)

    @classmethod
    def create_run_parser(cls):
        run_parser = _CLI._add_subparser("run", help="Run a Taipy application.")
        mode_group = run_parser.add_mutually_exclusive_group()
        for mode_arg, mode_arg_dict in cls.__MODE_ARGS.items():
            mode_group.add_argument(mode_arg, **mode_arg_dict)

        force_group = run_parser.add_mutually_exclusive_group()
        for force_arg, force_arg_dict in cls.__FORCE_ARGS.items():
            force_group.add_argument(force_arg, **force_arg_dict)

    @classmethod
    def parse_arguments(cls):
        args = _CLI._parse()
        as_dict = {}
        if args.taipy_development:
            as_dict[CoreSection._MODE_KEY] = CoreSection._DEVELOPMENT_MODE
        elif args.taipy_experiment is not None:
            as_dict[CoreSection._MODE_KEY] = CoreSection._EXPERIMENT_MODE
            as_dict[CoreSection._VERSION_NUMBER_KEY] = args.taipy_experiment
        elif args.taipy_production is not None:
            as_dict[CoreSection._MODE_KEY] = CoreSection._PRODUCTION_MODE
            as_dict[CoreSection._VERSION_NUMBER_KEY] = args.taipy_production

        if args.taipy_force:
            as_dict[CoreSection._FORCE_KEY] = True
        elif args.no_taipy_force:
            as_dict[CoreSection._FORCE_KEY] = False

        return as_dict

    @classmethod
    def __add_taipy_prefix(cls, key: str):
        if key.startswith("--no-"):
            return key[:5] + "taipy-" + key[5:]

        return key[:2] + "taipy-" + key[2:]
