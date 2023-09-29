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

from .migrate import _migrate_fs_entities


class _MigrateCLI:
    @classmethod
    def create_parser(cls):
        migrate_parser = _CLI._add_subparser(
            "migrate", help="Migrate entities from old taipy versions to current taipy version."
        )
        migrate_parser.add_argument("--path", help="The path to the File System Repository folder")

    @classmethod
    def parse_arguments(cls):
        args = _CLI._parse()

        if getattr(args, "which", None) == "migrate":
            path = sys.argv[-1]  # last argument is path to FS folder
            _migrate_fs_entities(path)

            sys.exit(0)
