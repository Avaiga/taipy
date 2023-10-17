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

import os
import sys

from taipy._cli._base_cli import _CLI
from taipy.logger._taipy_logger import _TaipyLogger

from ._migrate import _migrate_fs_entities, _migrate_mongo_entities, _migrate_sql_entities


class _MigrateCLI:
    __logger = _TaipyLogger._get_logger()

    @classmethod
    def create_parser(cls):
        migrate_parser = _CLI._add_subparser(
            "migrate",
            help="Migrate entities created from old taipy versions to be compatible with the current taipy version. "
            " The entity migration should be performed only after updating taipy code to the current version.",
        )
        migrate_parser.add_argument(
            "--repository-type",
            nargs="+",
            help="The type of repository to migrate. If filesystem or sql, a path to the database folder/.sqlite file "
            "should be informed. In case of mongo host, port, user and password must be informed, if left empty it "
            "is assumed default values",
        )

    @classmethod
    def parse_arguments(cls):
        args = _CLI._parse()

        if getattr(args, "which", None) != "migrate":
            return

        if args.repository_type:
            repository_type = args.repository_type[0]
            try:
                path = args.repository_type[1]
            except IndexError:
                path = None

            if repository_type == "filesystem":
                path = path or ".data"
                if not os.path.isdir(path):
                    cls.__logger.error(f"Folder '{path}' does not exist.")
                    sys.exit(1)
                _migrate_fs_entities(path)
            elif repository_type == "sql":
                if not path:
                    cls.__logger.error("Missing the required sqlite path.")
                    sys.exit(1)
                if not os.path.exists(path):
                    cls.__logger.error(f"File '{path}' does not exist.")
                    sys.exit(1)
                _migrate_sql_entities(path)
            elif repository_type == "mongo":
                mongo_args = args.repository_type[1:] if path else []
                _migrate_mongo_entities(*mongo_args)
            else:
                cls.__logger.error(f"Unknown repository type {repository_type}")
                sys.exit(1)
            sys.exit(0)
        elif getattr(args, "which", None) == "revert":
            if repository_type == "filesystem":
                path = path or ".data_backup"
                if not os.path.isdir(path):
                    cls.__logger.error(f"Folder '{path}' does not exist.")
                    sys.exit(1)
                _migrate_fs_entities(path)
            elif repository_type == "sql":
                if not path:
                    cls.__logger.error("Missing the required sqlite path.")
                    sys.exit(1)
                if not os.path.exists(path):
                    cls.__logger.error(f"File '{path}' does not exist.")
                    sys.exit(1)
                _migrate_sql_entities(path)
            # elif repository_type == "mongo":
            #     mongo_args = args.repository_type[1:] if path else []
            #     _migrate_mongo_entities(*mongo_args)
            # else:
            #     cls.__logger.error(f"Unknown repository type {repository_type}")
            #     sys.exit(1)
