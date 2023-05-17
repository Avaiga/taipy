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

from ...exceptions.exceptions import VersionIsNotProductionVersion
from ...taipy import clean_all_entities_by_version
from .._version_manager_factory import _VersionManagerFactory
from ._bcolor import _Bcolors


class _VersionCLI:
    """Command-line interface of the versioning system."""

    __logger = _TaipyLogger._get_logger()

    @classmethod
    def create_parser(cls):
        version_parser = _CLI._add_subparser("manage-versions", help="Taipy version control system.")

        version_parser.add_argument(
            "-l", "--list", action="store_true", help="List all existing versions of the Taipy application."
        )

        version_parser.add_argument(
            "-d", "--delete", metavar="VERSION", help="Delete a Taipy version by version number."
        )

        version_parser.add_argument(
            "-dp",
            "--delete-production",
            metavar="VERSION",
            help="Delete a Taipy version from production by version number. The version is still kept as an experiment "
            "version.",
        )

    @classmethod
    def parse_arguments(cls):
        args = _CLI._parse()

        if getattr(args, "which", None) != "manage-versions":
            return

        if args.list:
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

            print(list_version_message)
            sys.exit(0)

        if args.delete_production:
            try:
                _VersionManagerFactory._build_manager()._delete_production_version(args.delete_production)
                cls.__logger.info(f"Successfully delete version {args.delete_production} from production version list.")
                sys.exit(0)
            except VersionIsNotProductionVersion as e:
                raise SystemExit(e)

        if args.delete:
            if clean_all_entities_by_version(args.delete):
                cls.__logger.info(f"Successfully delete version {args.delete}.")
            else:
                sys.exit(1)

            sys.exit(0)
