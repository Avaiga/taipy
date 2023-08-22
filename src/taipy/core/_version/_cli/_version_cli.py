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
from taipy.config import Config
from taipy.config.exceptions.exceptions import InconsistentEnvVariableError
from taipy.logger._taipy_logger import _TaipyLogger

from ...data._data_manager_factory import _DataManagerFactory
from ...exceptions.exceptions import VersionIsNotProductionVersion
from ...job._job_manager_factory import _JobManagerFactory
from ...scenario._scenario_manager_factory import _ScenarioManagerFactory
from ...sequence._sequence_manager_factory import _SequenceManagerFactory
from ...taipy import clean_all_entities_by_version
from ...task._task_manager_factory import _TaskManagerFactory
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
            print(cls.__list_versions())
            sys.exit(0)

        if args.rename:
            try:
                cls.__rename_version(args.rename[0], args.rename[1])
            except InconsistentEnvVariableError as error:
                cls.__logger.error(
                    f"Fail to rename version {args.rename[0]} to {args.rename[1]} due to outdated Configuration."
                    f"Detail: {str(error)}"
                )
                sys.exit(1)

            cls.__logger.info(f"Successfully renamed version '{args.rename[0]}' to '{args.rename[1]}'.")
            sys.exit(0)

        if args.compare_config:
            cls.__compare_version_config(args.compare_config[0], args.compare_config[1])
            sys.exit(0)

        if args.delete_production:
            try:
                _VersionManagerFactory._build_manager()._delete_production_version(args.delete_production)
                cls.__logger.info(
                    f"Successfully delete version {args.delete_production} from the production version list."
                )
                sys.exit(0)
            except VersionIsNotProductionVersion as e:
                raise SystemExit(e)

        if args.delete:
            if clean_all_entities_by_version(args.delete):
                cls.__logger.info(f"Successfully delete version {args.delete}.")
            else:
                sys.exit(1)

            sys.exit(0)

    @classmethod
    def __list_versions(cls):
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

        return list_version_message

    @classmethod
    def __rename_version(cls, old_version: str, new_version: str):
        _version_manager = _VersionManagerFactory._build_manager()

        # Check if the new version already exists, return an error
        if _version_manager._get(new_version):
            cls.__logger.error(f"Version name '{new_version}' is already used.")
            sys.exit(1)

        # Make sure that all entities of the old version are exists and loadable
        version_entity = _version_manager._get(old_version)
        if version_entity is None:
            cls.__logger.error(f"Version '{old_version}' does not exist.")
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

        # Update the version entity
        if old_version in _version_manager._get_production_versions():
            _version_manager._set_production_version(new_version)
        if old_version == _version_manager._get_latest_version():
            _version_manager._set_experiment_version(new_version)
        if old_version == _version_manager._get_development_version():
            _version_manager._set_development_version(new_version)
        _version_manager._delete(old_version)

        try:
            _version_manager._delete_production_version(old_version)
        except VersionIsNotProductionVersion:
            pass
        version_entity.id = new_version
        _version_manager._set(version_entity)

    @classmethod
    def __compare_version_config(cls, version_1: str, version_2: str):
        version_entity_1 = _VersionManagerFactory._build_manager()._get(version_1)
        if version_entity_1 is None:
            cls.__logger.error(f"Version '{version_1}' does not exist.")
            sys.exit(1)

        version_entity_2 = _VersionManagerFactory._build_manager()._get(version_2)
        if version_entity_2 is None:
            cls.__logger.error(f"Version '{version_2}' does not exist.")
            sys.exit(1)

        Config._comparator._compare(
            version_entity_1.config,
            version_entity_2.config,
            version_1,
            version_2,
        )
