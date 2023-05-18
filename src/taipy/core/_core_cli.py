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

from taipy._cli._base_cli import _CLI

from .config import CoreSection


class _CoreCLI:
    """Command-line interface for Taipy Core application."""

    @classmethod
    def create_parser(cls):
        core_parser = _CLI._add_groupparser("Taipy Core", "Optional arguments for Taipy Core service")

        mode_group = core_parser.add_mutually_exclusive_group()
        mode_group.add_argument(
            "--development",
            action="store_true",
            help="""
                When execute Taipy application in `development` mode, all entities from the previous development version
                will be deleted before running new Taipy application.
            """,
        )
        mode_group.add_argument(
            "--experiment",
            nargs="?",
            const="",
            metavar="VERSION",
            help="""
                When execute Taipy application in `experiment` mode, the current Taipy application is saved to a new
                version. If version name already exists, check for compatibility with current Python Config and run the
                application. Without being specified, the version number will be a random string.
            """,
        )
        mode_group.add_argument(
            "--production",
            nargs="?",
            const="",
            metavar="VERSION",
            help="""
                When execute in `production` mode, the current version is used in production. All production versions
                should have the same configuration and share all entities. Without being specified, the latest version
                is used.
            """,
        )

        force_group = core_parser.add_mutually_exclusive_group()
        force_group.add_argument(
            "--taipy-force",
            action="store_true",
            help="Force override the configuration of the version if existed and run the application."
            " Default to False.",
        )
        force_group.add_argument(
            "--no-taipy-force",
            action="store_true",
            help="Stop the application if any Config conflict exists.",
        )

        clean_entities_group = core_parser.add_mutually_exclusive_group()
        clean_entities_group.add_argument(
            "--clean-entities",
            action="store_true",
            help="Clean all current version entities before running the application. Default to False.",
        )
        clean_entities_group.add_argument(
            "--no-clean-entities",
            action="store_true",
            help="Keep all entities of the current experiment version.",
        )

    @classmethod
    def parse_arguments(cls):
        args = _CLI._parse()
        as_dict = {}
        if args.development:
            as_dict[CoreSection._MODE_KEY] = CoreSection._DEVELOPMENT_MODE
        elif args.experiment is not None:
            as_dict[CoreSection._MODE_KEY] = CoreSection._EXPERIMENT_MODE
            as_dict[CoreSection._VERSION_NUMBER_KEY] = args.experiment
        elif args.production is not None:
            as_dict[CoreSection._MODE_KEY] = CoreSection._PRODUCTION_MODE
            as_dict[CoreSection._VERSION_NUMBER_KEY] = args.production

        if args.taipy_force:
            as_dict[CoreSection._TAIPY_FORCE_KEY] = True
        elif args.no_taipy_force:
            as_dict[CoreSection._TAIPY_FORCE_KEY] = False

        if args.clean_entities:
            as_dict[CoreSection._CLEAN_ENTITIES_KEY] = True
        elif args.no_clean_entities:
            as_dict[CoreSection._CLEAN_ENTITIES_KEY] = False
        return as_dict
