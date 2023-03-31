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

from taipy.config.common._argparser import _Argparser

from ..exceptions.exceptions import VersionIsNotProductionVersion
from ..taipy import clean_all_entities_by_version
from ._bcolor import _Bcolors
from ._version_manager_factory import _VersionManagerFactory


class _VersioningCLI:
    """Command-line interface of the versioning system."""

    @classmethod
    def _create_parser(cls):
        core_parser = _Argparser._add_groupparser("Core", "Optional arguments for Core service")

        mode_group = core_parser.add_mutually_exclusive_group()
        mode_group.add_argument(
            "--development",
            "-dev",
            action="store_true",
            default=True,
            help="""
                When execute Taipy application in `development` mode, all entities from the previous development version
                will be deleted before running new Taipy application. This is the default behavior.
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

        core_parser.add_argument(
            "--force",
            "-f",
            action="store_true",
            help="Force override the configuration of the version if existed. Default to False.",
        )

        core_parser.add_argument(
            "--clean-entities",
            action="store_true",
            help="Clean all current version entities before running the application. Default to False.",
        )

        core_parser.add_argument(
            "--list-versions", "-l", action="store_true", help="List all existing versions of the Taipy application."
        )

        core_parser.add_argument(
            "--delete-version", "-d", metavar="VERSION", help="Delete a Taipy version by version number."
        )

        core_parser.add_argument(
            "--delete-production-version",
            "-dp",
            metavar="VERSION",
            help="Delete a Taipy version from production by version number. The version is still kept as an experiment "
            "version.",
        )

    @classmethod
    def _parse_arguments(cls):
        args = _Argparser._parse()

        if args.list_versions:
            list_version_message = f"\n{'Version number':<36}   {'Mode':<20}   {'Creation date':<20}\n"

            latest_version_number = _VersionManagerFactory._build_manager()._get_latest_version()
            development_version_number = _VersionManagerFactory._build_manager()._get_development_version()
            production_version_numbers = _VersionManagerFactory._build_manager()._get_production_versions()

            versions = _VersionManagerFactory._build_manager()._get_all()
            versions.sort(key=lambda x: x.creation_date, reverse=True)

            bold = False
            for version in versions:
                if version.id == development_version_number:
                    list_version_message += _Bcolors.GREEN
                    mode = "Development"
                elif version.id in production_version_numbers:
                    list_version_message += _Bcolors.PURPLE
                    mode = "Production"
                else:
                    list_version_message += _Bcolors.BLUE
                    mode = "Experiment"

                if version.id == latest_version_number:
                    list_version_message += _Bcolors.BOLD
                    bold = True
                    mode += " (latest)"

                list_version_message += (
                    f"{(version.id):<36}   {mode:<20}   {version.creation_date.strftime('%Y-%m-%d %H:%M:%S'):<20}"
                )
                list_version_message += _Bcolors.END
                if bold:
                    list_version_message += _Bcolors.END
                list_version_message += "\n"

            raise SystemExit(list_version_message)

        if args.delete_production_version:
            try:
                _VersionManagerFactory._build_manager()._delete_production_version(args.delete_production_version)
                raise SystemExit(
                    f"Successfully delete version {args.delete_production_version} from production version list."
                )
            except VersionIsNotProductionVersion as e:
                raise SystemExit(e)

        if args.delete_version:
            clean_all_entities_by_version(args.delete_version)
            raise SystemExit(f"Successfully delete version {args.delete_version}.")

        if args.development:
            mode = "development"
            version_number = ""
        if args.experiment is not None:
            version_number = args.experiment
            mode = "experiment"
        if args.production is not None:
            version_number = args.production
            mode = "production"

        return mode, version_number, args.force, args.clean_entities
