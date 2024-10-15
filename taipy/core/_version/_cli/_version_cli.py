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
from importlib.util import find_spec

from taipy.common._cli._base_cli._abstract_cli import _AbstractCLI
from taipy.common._cli._base_cli._taipy_parser import _TaipyParser
from taipy.common.config import Config
from taipy.common.config.exceptions.exceptions import InconsistentEnvVariableError

from ...data._data_manager_factory import _DataManagerFactory
from ...job._job_manager_factory import _JobManagerFactory
from ...scenario._scenario_manager_factory import _ScenarioManagerFactory
from ...sequence._sequence_manager_factory import _SequenceManagerFactory
from ...taipy import clean_all_entities
from ...task._task_manager_factory import _TaskManagerFactory
from .._version_manager_factory import _VersionManagerFactory
from ._bcolor import _Bcolors


class _VersionCLI(_AbstractCLI):
    """Command-line interface of the versioning system."""

    _COMMAND_NAME = "manage-versions"
    _ARGUMENTS = ["-l", "--list", "--rename", "--compare-config", "-d", "--delete"]

    @classmethod
    def create_parser(cls):
        version_parser = _TaipyParser._add_subparser(cls._COMMAND_NAME, help="Taipy version control system.")

        version_parser.add_argument(
            "-l", "--list", action="store_true", help="List all existing versions of the Taipy application."
        )

        version_parser.add_argument(
            "--rename", nargs=2, metavar=("OLD_VERSION", "NEW_VERSION"), help="Rename a Taipy version."
        )

        version_parser.add_argument(
            "--compare-config",
            nargs=2,
            metavar=("VERSION_1", "VERSION_2"),
            help="Compare the Configuration of 2 Taipy versions.",
        )

        version_parser.add_argument(
            "-d", "--delete", metavar="VERSION", help="Delete a Taipy version by version number."
        )

    @classmethod
    def handle_command(cls):
        args = cls._parse_arguments()
        if not args:
            return

        if args.list:
            print(cls.__list_versions())  # noqa: T201
            sys.exit(0)

        if args.rename:
            try:
                cls.__rename_version(args.rename[0], args.rename[1])
            except InconsistentEnvVariableError as error:
                cls._logger.error(
                    f"Fail to rename version {args.rename[0]} to {args.rename[1]} due to outdated Configuration."
                    f"Detail: {str(error)}"
                )
                sys.exit(1)

            cls._logger.info(f"Successfully renamed version '{args.rename[0]}' to '{args.rename[1]}'.")
            sys.exit(0)

        if args.compare_config:
            cls.__compare_version_config(args.compare_config[0], args.compare_config[1])
            sys.exit(0)

        if args.delete:
            if clean_all_entities(args.delete):
                cls._logger.info(f"Successfully delete version {args.delete}.")
            else:
                sys.exit(1)

            sys.exit(0)

    @classmethod
    def __list_versions(cls):
        list_version_message = f"\n{'Version number':<36}   {'Mode':<20}   {'Creation date':<20}\n"

        latest_version_number = _VersionManagerFactory._build_manager()._get_latest_version()
        development_version_number = _VersionManagerFactory._build_manager()._get_development_version()
        if find_spec("taipy.enterprise"):
            production_version_numbers = _VersionManagerFactory._build_manager()._get_production_versions()
        else:
            production_version_numbers = []

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

        return list_version_message

    @classmethod
    def __rename_version(cls, old_version: str, new_version: str):
        _version_manager = _VersionManagerFactory._build_manager()

        # Check if the new version already exists, return an error
        if _version_manager._get(new_version):
            cls._logger.error(f"Version name '{new_version}' is already used.")
            sys.exit(1)

        # Make sure that all entities of the old version are exists and loadable
        version_entity = _version_manager._get(old_version)
        if version_entity is None:
            cls._logger.error(f"Version '{old_version}' does not exist.")
            sys.exit(1)

        jobs = _JobManagerFactory._build_manager()._get_all(version_number=old_version)
        scenarios = _ScenarioManagerFactory._build_manager()._get_all(version_number=old_version)
        sequences = _SequenceManagerFactory._build_manager()._get_all(version_number=old_version)
        tasks = _TaskManagerFactory._build_manager()._get_all(version_number=old_version)
        datanodes = _DataManagerFactory._build_manager()._get_all(version_number=old_version)

        # Update the version of all entities
        for job in jobs:
            job._version = new_version
            _JobManagerFactory._build_manager()._set(job)
        for scenario in scenarios:
            scenario._version = new_version
            _ScenarioManagerFactory._build_manager()._set(scenario)
        for sequence in sequences:
            sequence._version = new_version
            _SequenceManagerFactory._build_manager()._set(sequence)
        for task in tasks:
            task._version = new_version
            _TaskManagerFactory._build_manager()._set(task)
        for datanode in datanodes:
            datanode._version = new_version
            _DataManagerFactory._build_manager()._set(datanode)

        # Rename the _Version entity
        _version_manager._rename_version(old_version, new_version)

    @classmethod
    def __compare_version_config(cls, version_1: str, version_2: str):
        version_entity_1 = _VersionManagerFactory._build_manager()._get(version_1)
        if version_entity_1 is None:
            cls._logger.error(f"Version '{version_1}' does not exist.")
            sys.exit(1)

        version_entity_2 = _VersionManagerFactory._build_manager()._get(version_2)
        if version_entity_2 is None:
            cls._logger.error(f"Version '{version_2}' does not exist.")
            sys.exit(1)

        Config._comparator._compare(  # type: ignore[attr-defined]
            version_entity_1.config,
            version_entity_2.config,
            version_1,
            version_2,
        )
