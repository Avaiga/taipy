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

import pathlib
import sys
from typing import Dict, Optional

from cookiecutter.exceptions import OutputDirExistsException
from cookiecutter.main import cookiecutter

import taipy

from ._base_cli._abstract_cli import _AbstractCLI
from ._base_cli._taipy_parser import _TaipyParser


class _CreateCLI(_AbstractCLI):
    _template_map: Dict[str, str] = {}

    _COMMAND_NAME = "create"
    _ARGUMENTS = ["--application"]

    @classmethod
    def generate_template_map(cls, template_path: Optional[pathlib.Path] = None):
        if not template_path:
            template_path = pathlib.Path(taipy.__file__).parent.resolve() / "templates"

        # Update the template map with the new templates but do not override the existing ones
        cls._template_map.update(
            {
                str(x.name): str(x)
                for x in template_path.iterdir()
                if x.is_dir() and not x.name.startswith("_") and x.name not in cls._template_map
            }
        )

    @classmethod
    def create_parser(cls):
        create_parser = _TaipyParser._add_subparser(
            cls._COMMAND_NAME,
            help="Create a new Taipy application using pre-defined templates.",
        )
        create_parser.add_argument(
            "--application",
            choices=list(cls._template_map.keys()),
            default="default",
            help="The template used to create the new Taipy application.",
        )

    @classmethod
    def handle_command(cls):
        args = cls._parse_arguments()
        if not args:
            return
        try:
            cookiecutter(cls._template_map[args.application])
        except OutputDirExistsException as err:
            error_msg = f"{str(err)}. Please remove the existing directory or provide a new folder name."
            print(error_msg)  # noqa: T201
            sys.exit(1)
        sys.exit(0)
