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
from typing import List

from taipy.common._cli._base_cli._abstract_cli import _AbstractCLI
from taipy.common._cli._base_cli._taipy_parser import _TaipyParser
from taipy.common.config import Config

from ._migrate import (
    _migrate_fs_entities,
    _migrate_mongo_entities,
    _remove_backup_file_entities,
    _remove_backup_mongo_entities,
    _restore_migrate_file_entities,
    _restore_migrate_mongo_entities,
)


class _MigrateCLI(_AbstractCLI):
    _COMMAND_NAME = "migrate"
    _ARGUMENTS = ["--repository-type", "--skip-backup", "--restore", "--remove-backup"]

    @classmethod
    def create_parser(cls):
        migrate_parser = _TaipyParser._add_subparser(
            cls._COMMAND_NAME,
            help="Migrate entities created from old taipy versions to be compatible with the current taipy version. "
            " The entity migration should be performed only after updating taipy code to the current version.",
        )
        migrate_parser.add_argument(
            "--repository-type",
            nargs="+",
            help="The type of repository to migrate. If filesystem, a path to the database folder should be informed. "
            "In case of mongo host, port, user and password must be informed, if left empty it "
            "is assumed default values",
        )
        migrate_parser.add_argument(
            "--skip-backup",
            action="store_true",
            help="Skip the backup of entities before migration.",
        )
        migrate_parser.add_argument(
            "--restore",
            action="store_true",
            help="Restore the migration of entities from backup folder.",
        )
        migrate_parser.add_argument(
            "--remove-backup",
            action="store_true",
            help="Remove the backup of entities. Only use this option if the migration was successful.",
        )

    @classmethod
    def handle_command(cls):
        args = cls._parse_arguments()
        if not args:
            return

        if not args.repository_type:
            _TaipyParser._sub_taipyparsers.get(cls._COMMAND_NAME).print_help()
            cls._logger.error("The following arguments are required: --repository-type")
            sys.exit(1)

        repository_type = args.repository_type[0]
        repository_args = args.repository_type[1:] if len(args.repository_type) > 1 else [None]

        if args.restore:
            cls.__handle_restore_backup(repository_type, repository_args)
        if args.remove_backup:
            cls.__handle_remove_backup(repository_type, repository_args)

        do_backup = not args.skip_backup
        cls.__migrate_entities(repository_type, repository_args, do_backup)
        sys.exit(0)

    @classmethod
    def __handle_remove_backup(cls, repository_type: str, repository_args: List):
        if repository_type == "filesystem":
            path = repository_args[0] or Config.core.taipy_storage_folder
            if not _remove_backup_file_entities(path):
                sys.exit(1)
        elif repository_type == "mongo":
            if not _remove_backup_mongo_entities():
                sys.exit(1)
        else:
            cls._logger.error(f"Unknown repository type {repository_type}")
            sys.exit(1)

        sys.exit(0)

    @classmethod
    def __handle_restore_backup(cls, repository_type: str, repository_args: List):
        if repository_type == "filesystem":
            path = repository_args[0] or Config.core.taipy_storage_folder
            if not _restore_migrate_file_entities(path):
                sys.exit(1)
        elif repository_type == "mongo":
            mongo_args = repository_args[1:5] if repository_args[0] else []
            if not _restore_migrate_mongo_entities(*mongo_args):
                sys.exit(1)
        else:
            cls._logger.error(f"Unknown repository type {repository_type}")
            sys.exit(1)
        sys.exit(0)

    @classmethod
    def __migrate_entities(cls, repository_type: str, repository_args: List, do_backup: bool):
        if repository_type == "filesystem":
            path = repository_args[0] or Config.core.taipy_storage_folder
            if not _migrate_fs_entities(path, do_backup):
                sys.exit(1)

        elif repository_type == "mongo":
            mongo_args = repository_args[1:5] if repository_args[0] else []
            _migrate_mongo_entities(*mongo_args, backup=do_backup)  # type: ignore

        else:
            cls._logger.error(f"Unknown repository type {repository_type}")
            sys.exit(1)
